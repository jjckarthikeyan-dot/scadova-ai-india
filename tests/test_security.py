from backend.core.security import (
    UserRole,
    create_access_token,
    decode_access_token,
    get_password_hash,
    mask_aadhaar,
    mask_bank_account,
    mask_mobile,
    mask_pan,
    redact_sensitive_payload,
    verify_password,
)


def test_password_hashing():
    raw_password = "SecurePassword123!"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_flow():
    user_payload = {
        "sub": "user-uuid-12345",
        "email": "analyst@scadova.ai",
        "role": UserRole.ANALYST.value,
    }
    token = create_access_token(user_payload)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-uuid-12345"
    assert decoded["role"] == UserRole.ANALYST.value
    assert decoded["email"] == "analyst@scadova.ai"


def test_sensitive_data_masking():
    # PAN masking
    pan = "ABCDE1234F"
    masked_pan = mask_pan(pan)
    assert masked_pan == "AB******4F"

    # Aadhaar masking
    aadhaar = "987654321098"
    masked_aadhaar = mask_aadhaar(aadhaar)
    assert masked_aadhaar == "********1098"

    # Bank Account masking
    account = "123456789012"
    masked_acc = mask_bank_account(account)
    assert masked_acc == "********9012"

    # Mobile masking
    mobile = "9876543210"
    masked_mob = mask_mobile(mobile)
    assert masked_mob == "******3210"


def test_redact_sensitive_payload():
    payload = {
        "pan": "ABCDE1234F",
        "aadhaar": "987654321098",
        "password": "secretpassword",
        "jwt_token": "secrettoken",
        "mobile": "9876543210",
        "nested": {
            "bank_account": "123456789012",
            "safe_field": "public_data",
        },
    }
    redacted = redact_sensitive_payload(payload)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["jwt_token"] == "[REDACTED]"
    assert "******" in redacted["pan"]
    assert "********" in redacted["aadhaar"]
    assert "******" in redacted["mobile"]
    assert "********" in redacted["nested"]["bank_account"]
    assert redacted["nested"]["safe_field"] == "public_data"
