"""WebSocket endpoint for real-time notifications."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.notification_service import notifications
from utils.jwt_util import decode_token


notification_router = APIRouter(tags=["notifications"])


@notification_router.websocket("/ws/notifications")
async def notification_socket(websocket: WebSocket):
    payload = decode_token(websocket.query_params.get("token", ""))
    if not payload:
        await websocket.close(code=4401)
        return

    await notifications.connect(
        websocket,
        int(payload["user_id"]),
        payload.get("role", "user"),
    )
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notifications.disconnect(websocket)
    except Exception:
        notifications.disconnect(websocket)
