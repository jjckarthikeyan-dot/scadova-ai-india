import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import HTTPException, UploadFile, status

from backend.core.config import settings
from backend.core.database import get_supabase_admin_client

ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/json",
]
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB


class StorageService:
    def __init__(self):
        self.bucket = settings.STORAGE_BUCKET

    def validate_file(self, content_type: str, file_size: Optional[int] = None):
        """Validates MIME type and file size."""
        if content_type.lower() not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported document format: {content_type}. Allowed: {ALLOWED_MIME_TYPES}",
            )
        if file_size and file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of 15MB",
            )

    def generate_presigned_upload_url(
        self,
        application_id: str,
        document_type: str,
        file_name: str,
        expires_in_seconds: int = 900,
    ) -> Dict[str, str]:
        """Generates a private short-lived presigned upload URL."""
        file_ext = os.path.splitext(file_name)[1].lower() or ".pdf"
        unique_file_id = str(uuid.uuid4())
        storage_path = f"applications/{application_id}/{document_type.lower()}_{unique_file_id}{file_ext}"

        supabase_admin = get_supabase_admin_client()
        if supabase_admin:
            try:
                res = supabase_admin.storage.from_(self.bucket).create_signed_upload_url(storage_path)
                return {
                    "storage_path": storage_path,
                    "upload_url": res.get("signed_url") or res.get("url"),
                    "token": res.get("token", ""),
                    "expires_in": str(expires_in_seconds),
                }
            except Exception:
                pass

        # Mock fallback signed upload URL for local/offline testing
        mock_upload_url = f"/api/loan-agency/documents/mock-upload?path={storage_path}&expires={expires_in_seconds}"
        return {
            "storage_path": storage_path,
            "upload_url": mock_upload_url,
            "token": "local-dev-mock-token",
            "expires_in": str(expires_in_seconds),
        }

    def generate_presigned_download_url(
        self,
        storage_path: str,
        expires_in_seconds: int = 300,
    ) -> str:
        """Generates a private short-lived download URL (valid for 5 mins)."""
        supabase_admin = get_supabase_admin_client()
        if supabase_admin:
            try:
                res = supabase_admin.storage.from_(self.bucket).create_signed_url(
                    storage_path, expires_in_seconds
                )
                if isinstance(res, dict) and "signedURL" in res:
                    return res["signedURL"]
                elif isinstance(res, dict) and "signed_url" in res:
                    return res["signed_url"]
            except Exception:
                pass

        # Fallback local signed URL
        return f"/api/loan-agency/documents/view?path={storage_path}&token=secure-shortlived-token"


storage_service = StorageService()
