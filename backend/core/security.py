import re
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union
import bcrypt
import jwt

from backend.core.config import settings


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    ANALYST = "ANALYST"
    AGENT = "AGENT"
    APPLICANT = "APPLICANT"


# Password Hashing Utilities using bcrypt
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


# JWT Utilities
def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except (jwt.PyJWTError, Exception):
        return None


# Sensitive Data Masking Helpers
def mask_pan(pan: Optional[str]) -> Optional[str]:
    """Masks PAN leaving first 2 and last 2 characters or standard format."""
    if not pan:
        return pan
    clean = pan.strip().upper()
    if len(clean) == 10:
        return f"{clean[:2]}******{clean[-2:]}"
    return "******" + clean[-4:] if len(clean) > 4 else "******"


def mask_aadhaar(aadhaar: Optional[str]) -> Optional[str]:
    """Masks Aadhaar leaving only last 4 digits visible."""
    if not aadhaar:
        return aadhaar
    clean = re.sub(r"\s+", "", aadhaar.strip())
    if len(clean) >= 4:
        return f"********{clean[-4:]}"
    return "********"


def mask_bank_account(account_number: Optional[str]) -> Optional[str]:
    """Masks Bank Account leaving only last 4 digits visible."""
    if not account_number:
        return account_number
    clean = account_number.strip()
    if len(clean) > 4:
        return f"{'*' * (len(clean) - 4)}{clean[-4:]}"
    return "****" + clean


def mask_mobile(mobile: Optional[str]) -> Optional[str]:
    """Masks Mobile Number leaving only last 4 digits visible."""
    if not mobile:
        return mobile
    clean = re.sub(r"[^\d]", "", mobile.strip())
    if len(clean) >= 10:
        return f"{'*' * (len(clean) - 4)}{clean[-4:]}"
    return "******" + clean[-4:] if len(clean) > 4 else "******"


def redact_sensitive_payload(payload: Any) -> Any:
    """Recursively redacts sensitive keys in dictionaries or lists for logging."""
    if isinstance(payload, dict):
        redacted = {}
        for k, v in payload.items():
            key_lower = k.lower()
            if any(term in key_lower for term in ["password", "token", "secret", "key"]):
                redacted[k] = "[REDACTED]"
            elif "pan" in key_lower:
                redacted[k] = mask_pan(str(v)) if v else v
            elif "aadhaar" in key_lower:
                redacted[k] = mask_aadhaar(str(v)) if v else v
            elif "account_number" in key_lower or "bank_account" in key_lower:
                redacted[k] = mask_bank_account(str(v)) if v else v
            elif "mobile" in key_lower or "phone" in key_lower:
                redacted[k] = mask_mobile(str(v)) if v else v
            else:
                redacted[k] = redact_sensitive_payload(v)
        return redacted
    elif isinstance(payload, list):
        return [redact_sensitive_payload(item) for item in payload]
    return payload
