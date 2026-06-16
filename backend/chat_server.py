import json
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="Campus Errand Chat", version="1.0.0")
CHAT_STORE = Path(__file__).with_name("chat_messages.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    id: str
    room: str
    sender: str
    text: str
    created_at: str


class SendMessage(BaseModel):
    room: str = Field(default="general", min_length=1, max_length=64)
    sender: str = Field(default="用户", min_length=1, max_length=32)
    text: str = Field(min_length=1, max_length=1000)


class ConnectionManager:
    def __init__(self) -> None:
        self.active: dict[str, set[WebSocket]] = defaultdict(set)
        self.history: dict[str, Deque[ChatMessage]] = defaultdict(lambda: deque(maxlen=100))
        self.load()

    def load(self) -> None:
        if not CHAT_STORE.exists():
            return

        try:
            data = json.loads(CHAT_STORE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        for room, messages in data.items():
            self.history[room] = deque(
                [ChatMessage(**message) for message in messages],
                maxlen=100,
            )

    def persist(self) -> None:
        data = {
            room: [message.model_dump() for message in messages]
            for room, messages in self.history.items()
        }
        CHAT_STORE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    async def connect(self, room: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active[room].add(websocket)

    def disconnect(self, room: str, websocket: WebSocket) -> None:
        self.active[room].discard(websocket)

    async def broadcast(self, message: ChatMessage) -> None:
        disconnected: list[WebSocket] = []
        for websocket in self.active[message.room]:
            try:
                await websocket.send_json(message.model_dump())
            except RuntimeError:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(message.room, websocket)

    async def save_and_broadcast(self, payload: SendMessage) -> ChatMessage:
        message = ChatMessage(
            id=str(uuid4()),
            room=payload.room.strip() or "general",
            sender=payload.sender.strip() or "用户",
            text=payload.text.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.history[message.room].append(message)
        self.persist()
        await self.broadcast(message)
        return message


manager = ConnectionManager()


@app.get("/api/chat/health")
async def health():
    return {"status": "ok"}


@app.get("/api/chat/history/{room}", response_model=list[ChatMessage])
async def history(room: str):
    return list(manager.history[room])


@app.post("/api/chat/messages", response_model=ChatMessage)
async def send_message(payload: SendMessage):
    return await manager.save_and_broadcast(payload)


@app.websocket("/ws/chat/{room}")
async def chat_socket(websocket: WebSocket, room: str):
    await manager.connect(room, websocket)
    try:
        for message in manager.history[room]:
            await websocket.send_json(message.model_dump())

        while True:
            payload = await websocket.receive_json()
            await manager.save_and_broadcast(SendMessage(room=room, **payload))
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("chat_server:app", host="0.0.0.0", port=8001, reload=True)
