from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError

from app.core.security import decode_token
from app.services.ws_manager import manager

router = APIRouter()


@router.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket, token: str = Query(...)):
    """Connect with ws://<host>/ws/notifications?token=<access_token>.

    After connecting, the client should send {"type": "location", "lat": ..,
    "lng": ..} whenever it knows the user's current position — that's how the
    server knows who's "nearby" for a given new post. No location, no live
    notifications for that connection (silently — this is not required for
    the rest of the app to work).
    """
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            await websocket.close(code=4401)
            return
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4401)
            return
    except JWTError:
        await websocket.close(code=4401)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "location":
                lat, lng = data.get("lat"), data.get("lng")
                if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
                    manager.update_location(user_id, websocket, lat, lng)
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
