from datetime import datetime, timezone
from typing import Dict, Optional
from sqlalchemy.orm import Session


class UsageTracker:
    def __init__(self):
        # In-memory tracking for lightweight usage counters
        self._counters: Dict[str, int] = {}

    def track_request(
        self,
        tenant_id: str,
        endpoint: str,
        user_id: Optional[str] = None,
        db: Optional[Session] = None,
    ):
        """Records endpoint call usage for rate limiting and billing analytics."""
        key = f"{tenant_id}:{endpoint}"
        self._counters[key] = self._counters.get(key, 0) + 1

    def get_tenant_usage(self, tenant_id: str) -> Dict[str, int]:
        """Returns total requests aggregated by endpoint for a given tenant."""
        result = {}
        prefix = f"{tenant_id}:"
        for k, v in self._counters.items():
            if k.startswith(prefix):
                endpoint = k[len(prefix):]
                result[endpoint] = v
        return result


usage_tracker = UsageTracker()
