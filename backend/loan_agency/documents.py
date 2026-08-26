from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.common.audit import log_audit_event
from backend.common.responses import success_response
from backend.common.storage import storage_service
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.loan_agency.repository import LoanAgencyRepository
from backend.loan_agency.schemas import (
    DocumentCompleteRequest,
    DocumentPresignRequest,
    DocumentPresignResponse,
    DocumentRead,
)

router = APIRouter()


@router.post("/{application_id}/presign")
def presign_document_upload(
    application_id: str,
    payload: DocumentPresignRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Generates a secure presigned upload URL for direct, private storage upload."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")

    storage_service.validate_file(payload.content_type, payload.file_size_bytes)
    presign_data = storage_service.generate_presigned_upload_url(
        application_id=application_id,
        document_type=payload.document_type.value,
        file_name=payload.file_name,
    )
    return success_response(presign_data)


@router.post("/{application_id}/complete", status_code=status.HTTP_201_CREATED)
def complete_document_upload(
    application_id: str,
    payload: DocumentCompleteRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Records document metadata and completes attachment to application."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")

    storage_service.validate_file(payload.mime_type, payload.file_size_bytes)
    doc = LoanAgencyRepository.save_document(
        db=db,
        application_id=application_id,
        document_type=payload.document_type.value,
        file_name=payload.file_name,
        storage_path=payload.storage_path,
        mime_type=payload.mime_type,
        file_size_bytes=payload.file_size_bytes,
    )
    log_audit_event(
        db,
        event_type="DOCUMENT_UPLOADED",
        entity_type="document",
        entity_id=doc.id,
        user_id=current_user.get("id"),
        details={"doc_type": doc.document_type, "file_name": doc.file_name},
    )
    return success_response(DocumentRead.model_validate(doc).model_dump())


@router.get("/{application_id}")
def list_application_documents(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lists all uploaded documents with short-lived secure download URLs."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")

    docs = LoanAgencyRepository.get_documents_by_application(db, application_id)
    results = []
    for d in docs:
        d_dict = DocumentRead.model_validate(d).model_dump()
        d_dict["download_url"] = storage_service.generate_presigned_download_url(d.storage_path)
        results.append(d_dict)

    return success_response(results)


@router.delete("/{application_id}/{document_id}")
def delete_document(
    application_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Deletes a document record from the loan application."""
    success = LoanAgencyRepository.delete_document(db, application_id, document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    log_audit_event(
        db,
        event_type="DOCUMENT_DELETED",
        entity_type="document",
        entity_id=document_id,
        user_id=current_user.get("id"),
    )
    return success_response({"deleted": True, "document_id": document_id})
