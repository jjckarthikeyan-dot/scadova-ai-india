from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar
import uuid
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = Field(default=True, description="Indicates if the operation succeeded")
    data: Optional[T] = Field(default=None, description="Response payload")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request tracing ID")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of the response",
    )


def success_response(data: Any = None, request_id: Optional[str] = None) -> dict:
    """Helper to return standard success dictionary envelope."""
    return {
        "success": True,
        "data": data if data is not None else {},
        "error": None,
        "request_id": request_id or str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def error_response(
    error: str,
    data: Any = None,
    request_id: Optional[str] = None
) -> dict:
    """Helper to return standard error dictionary envelope."""
    return {
        "success": False,
        "data": data,
        "error": error,
        "request_id": request_id or str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
