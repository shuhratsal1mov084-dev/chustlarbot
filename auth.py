from functools import wraps
from fastapi import Request, HTTPException, status
from config import ADMIN_PASSWORD


class SessionManager:
    def __init__(self):
        self.active_sessions = set()

    def create_session(self, session_id: str, password: str) -> bool:
        if password == ADMIN_PASSWORD:
            self.active_sessions.add(session_id)
            return True
        return False

    def verify_session(self, session_id: str) -> bool:
        return session_id in self.active_sessions

    def destroy_session(self, session_id: str):
        self.active_sessions.discard(session_id)


session_manager = SessionManager()


def require_auth(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        session_id = request.cookies.get("session_id")
        if not session_id or not session_manager.verify_session(session_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        return await func(request, *args, **kwargs)
    return wrapper
