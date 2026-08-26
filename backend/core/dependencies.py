from typing import List, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import UserRole, decode_access_token

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> dict:
    if not credentials:
        # Fallback default mock user for development/demo mode if unauthenticated
        return {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "agent@scadova.ai",
            "role": UserRole.AGENT.value,
            "full_name": "Scadova Agent",
            "is_active": True,
        }

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    role = payload.get("role", UserRole.AGENT.value)
    email = payload.get("email", "")

    return {
        "id": user_id or "00000000-0000-0000-0000-000000000001",
        "email": email,
        "role": role,
        "full_name": payload.get("name", "User"),
        "is_active": True,
    }


def require_role(allowed_roles: List[Union[UserRole, str]]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        string_roles = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]
        if user_role not in string_roles and UserRole.ADMIN.value not in string_roles and user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of {string_roles}",
            )
        return current_user

    return role_checker
