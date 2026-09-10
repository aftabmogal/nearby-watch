import math
from typing import Dict, List, Optional

from fastapi import WebSocket


class ConnectionManager:
    """In-memory WebSocket registry for MVP-scale real-time notifications.

    Single-process design: works great for local dev and a single-instance
    deployment (Render/Railway free tier). If this ever needs to run behind
    multiple worker processes, swap this class's internals for Redis pub/sub —
    callers (routers/posts.py, routers/comments.py) never touch `self.active`
    directly, so that swap wouldn't require changing any endpoint code.
    """

    def __init__(self) -> None:
        # user_id -> list of {"ws": WebSocket, "lat": float | None, "lng": float | None}
        self.active: Dict[str, List[dict]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(user_id, []).append(
            {"ws": websocket, "lat": None, "lng": None}
        )

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        conns = self.active.get(user_id, [])
        remaining = [c for c in conns if c["ws"] != websocket]
        if remaining:
            self.active[user_id] = remaining
        else:
            self.active.pop(user_id, None)

    def update_location(self, user_id: str, websocket: WebSocket, lat: float, lng: float) -> None:
        for c in self.active.get(user_id, []):
            if c["ws"] == websocket:
                c["lat"], c["lng"] = lat, lng

    @staticmethod
    def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        r = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lng2 - lng1)
        a = math.sin(d_phi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d_lambda / 2) ** 2
        return 2 * r * math.asin(math.sqrt(a))

    async def broadcast_near(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        message: dict,
        exclude_user_id: Optional[str] = None,
    ) -> List[str]:
        """Sends `message` to every connected user within radius_km of
        (lat, lng), except exclude_user_id. Returns the list of user_ids that
        were actually matched, so callers can persist a Notification record
        for them too."""
        matched: List[str] = []
        for user_id, conns in list(self.active.items()):
            if user_id == exclude_user_id:
                continue
            is_match = False
            for c in conns:
                if c["lat"] is None or c["lng"] is None:
                    continue
                if self._haversine_km(lat, lng, c["lat"], c["lng"]) <= radius_km:
                    is_match = True
                    try:
                        await c["ws"].send_json(message)
                    except Exception:
                        pass
            if is_match:
                matched.append(user_id)
        return matched

    async def send_to_user(self, user_id: str, message: dict) -> None:
        for c in self.active.get(user_id, []):
            try:
                await c["ws"].send_json(message)
            except Exception:
                pass


manager = ConnectionManager()
