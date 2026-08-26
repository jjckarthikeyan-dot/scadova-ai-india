import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from backend.core.security import redact_sensitive_payload

logger = logging.getLogger("audit")


def log_audit_event(
    db: Optional[Session],
    event_type: str,
    entity_type: str,
    entity_id: str,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
):
    """
    Logs an audit event with automatic redaction of any sensitive credentials or PII.
    Saves to the database when available and always emits a structured log.
    """
    safe_details = redact_sensitive_payload(details or {})
    event_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "ip_address": ip_address,
        "details": safe_details,
    }
    logger.info(f"AUDIT_EVENT: {json.dumps(event_payload)}")

    if db is not None:
        try:
            # We will insert into AuditEvent table if available
            from backend.loan_agency.models import AuditEvent
            audit_record = AuditEvent(
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                tenant_id=tenant_id,
                details=safe_details,
                ip_address=ip_address,
            )
            db.add(audit_record)
            db.commit()
        except Exception as e:
            logger.warning(f"Could not persist audit record to DB: {e}")
