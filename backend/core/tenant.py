import contextvars
from typing import Optional
from fastapi import Header, Request

# Context variable to hold the current tenant/organization ID across async tasks
tenant_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("tenant_id", default=None)


def get_current_tenant() -> Optional[str]:
    """Returns the current tenant ID from context."""
    return tenant_context.get()


def set_current_tenant(tenant_id: Optional[str]):
    """Sets the current tenant ID in context."""
    tenant_context.set(tenant_id)


async def tenant_dependency(
    request: Request,
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
) -> Optional[str]:
    """FastAPI dependency to extract tenant ID from headers or query parameters."""
    tenant_id = x_tenant_id or request.query_params.get("tenant_id") or "default"
    set_current_tenant(tenant_id)
    return tenant_id
