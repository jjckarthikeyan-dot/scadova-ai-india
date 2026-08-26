from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.common.audit import log_audit_event
from backend.common.pagination import PaginatedResult, PaginationParams
from backend.common.responses import success_response
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.core.tenant import tenant_dependency
from backend.loan_agency.models import LoanApplication
from backend.loan_agency.repository import LoanAgencyRepository
from backend.loan_agency.schemas import (
    ApplicationStatusEnum,
    LoanApplicationCreate,
    LoanApplicationRead,
    LoanApplicationUpdate,
    StatusTransitionRequest,
)
from backend.loan_agency.service import LoanAgencyService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_loan_application(
    payload: LoanApplicationCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(tenant_dependency),
    current_user: dict = Depends(get_current_user),
):
    """Creates a new loan application in DRAFT status."""
    app = LoanAgencyRepository.create_application(db, payload, tenant_id=tenant_id)
    log_audit_event(
        db,
        event_type="APPLICATION_CREATED",
        entity_type="loan_application",
        entity_id=app.id,
        user_id=current_user.get("id"),
        tenant_id=tenant_id,
        details={"loan_type": payload.loan_type.value, "amount": str(payload.requested_amount)},
    )
    return success_response(LoanApplicationRead.model_validate(app).model_dump())


@router.get("")
def list_loan_applications(
    loan_type: Optional[str] = Query(None, description="Filter by loan type"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(tenant_dependency),
    current_user: dict = Depends(get_current_user),
):
    """Lists loan applications with filtering and pagination."""
    skip = (page - 1) * limit
    apps = LoanAgencyRepository.list_applications(
        db, tenant_id=tenant_id, loan_type=loan_type, status=status_filter, skip=skip, limit=limit
    )
    total = LoanAgencyRepository.count_applications(
        db, tenant_id=tenant_id, loan_type=loan_type, status=status_filter
    )
    items = [LoanApplicationRead.model_validate(a).model_dump() for a in apps]
    paginated = PaginatedResult.create(items=items, total=total, page=page, limit=limit)
    return success_response(paginated.model_dump())


@router.get("/{application_id}")
def get_loan_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieves full application details by ID."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    return success_response(LoanApplicationRead.model_validate(app).model_dump())


@router.patch("/{application_id}")
def update_loan_application(
    application_id: str,
    payload: LoanApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Updates loan application details (requested amount, tenure, purpose)."""
    app = LoanAgencyRepository.update_application(db, application_id, payload)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    log_audit_event(
        db,
        event_type="APPLICATION_UPDATED",
        entity_type="loan_application",
        entity_id=app.id,
        user_id=current_user.get("id"),
        details=payload.model_dump(exclude_unset=True),
    )
    return success_response(LoanApplicationRead.model_validate(app).model_dump())


@router.delete("/{application_id}")
def delete_loan_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Soft or hard deletes an application."""
    success = LoanAgencyRepository.delete_application(db, application_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    log_audit_event(
        db,
        event_type="APPLICATION_DELETED",
        entity_type="loan_application",
        entity_id=application_id,
        user_id=current_user.get("id"),
    )
    return success_response({"deleted": True, "application_id": application_id})


@router.get("/{application_id}/missing-fields")
def get_application_missing_fields(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Analyzes application for missing mandatory fields or documents."""
    missing = LoanAgencyService.get_missing_fields(db, application_id)
    return success_response({"application_id": application_id, "missing_fields": missing, "is_ready": len(missing) == 0})


@router.post("/{application_id}/submit")
def submit_loan_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Submits application for underwriting review."""
    missing = LoanAgencyService.get_missing_fields(db, application_id)
    new_status = (
        ApplicationStatusEnum.READY_FOR_ANALYSIS.value
        if len(missing) == 0
        else ApplicationStatusEnum.DATA_PENDING.value
    )
    app = LoanAgencyRepository.update_status(
        db,
        application_id,
        new_status=new_status,
        user_id=current_user.get("id"),
        remarks="Application submitted for underwriting",
    )
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    return success_response(
        {
            "application_id": app.id,
            "status": app.status,
            "missing_fields": missing,
            "message": "Application submitted successfully",
        }
    )


@router.post("/{application_id}/status")
def transition_application_status(
    application_id: str,
    payload: StatusTransitionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Explicitly updates application workflow status."""
    app = LoanAgencyRepository.update_status(
        db,
        application_id,
        new_status=payload.new_status.value,
        user_id=current_user.get("id"),
        remarks=payload.remarks,
    )
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    log_audit_event(
        db,
        event_type="STATUS_CHANGED",
        entity_type="loan_application",
        entity_id=application_id,
        user_id=current_user.get("id"),
        details={"new_status": payload.new_status.value, "remarks": payload.remarks},
    )
    return success_response(
        {
            "application_id": app.id,
            "status": app.status,
            "remarks": payload.remarks,
        }
    )
