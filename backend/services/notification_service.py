"""In-memory WebSocket connections and order notification delivery."""

from collections import defaultdict
from typing import Any

from fastapi import WebSocket
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.rider import Rider


class NotificationService:
    def __init__(self):
        self._users: dict[int, set[WebSocket]] = defaultdict(set)
        self._roles: dict[str, set[WebSocket]] = defaultdict(set)
        self._metadata: dict[WebSocket, tuple[int, str]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, role: str):
        await websocket.accept()
        self._users[user_id].add(websocket)
        self._roles[role].add(websocket)
        self._metadata[websocket] = (user_id, role)

    def disconnect(self, websocket: WebSocket):
        metadata = self._metadata.pop(websocket, None)
        if not metadata:
            return
        user_id, role = metadata
        self._users[user_id].discard(websocket)
        self._roles[role].discard(websocket)

    async def send_user(self, user_id: int, payload: dict[str, Any]):
        await self._send(self._users.get(user_id, set()), payload)

    async def send_role(self, role: str, payload: dict[str, Any]):
        await self._send(self._roles.get(role, set()), payload)

    async def _send(self, sockets: set[WebSocket], payload: dict[str, Any]):
        for websocket in list(sockets):
            try:
                await websocket.send_json(payload)
            except Exception:
                self.disconnect(websocket)


notifications = NotificationService()


async def publish_order_event(
    db: AsyncSession,
    event_type: str,
    order,
    message: str,
):
    payload = {
        "type": event_type,
        "message": message,
        "order_id": order.order_id,
        "order_no": order.order_no,
        "status": order.status,
        "order_type": order.order_type,
    }
    await notifications.send_user(order.publisher_id, payload)

    if order.rider_id:
        result = await db.execute(
            select(Rider.user_id).where(Rider.rider_id == order.rider_id)
        )
        rider_user_id = result.scalar_one_or_none()
        if rider_user_id:
            await notifications.send_user(rider_user_id, payload)

    if event_type in {"order_created", "order_accepted", "order_cancelled"}:
        await notifications.send_role("rider", payload)
