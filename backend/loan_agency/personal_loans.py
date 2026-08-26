from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.common.audit import log_audit_event
from backend.common.responses import success_response
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.loan_agency.repository import LoanAgencyRepository
from backend.loan_agency.schemas import (
    LoanProductEnum,
    PersonalLoanProfileRead,
    PersonalLoanProfileUpdate,
)

router = APIRouter()


@router.put("/{application_id}")
def update_personal_loan_profile(
    application_id: str,
    payload: PersonalLoanProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Saves or updates personal salaried loan profile data."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    if app.loan_type != LoanProductEnum.PERSONAL_LOAN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application {application_id} is for {app.loan_type}, not PERSONAL_LOAN",
        )

    profile = LoanAgencyRepository.save_personal_profile(db, application_id, payload)
    log_audit_event(
        db,
        event_type="PERSONAL_PROFILE_UPDATED",
        entity_type="employment_profile",
        entity_id=profile.id,
        user_id=current_user.get("id"),
        details=payload.model_dump(mode="json"),
    )
    return success_response(PersonalLoanProfileRead.model_validate(profile).model_dump())


@router.get("/{application_id}")
def get_personal_loan_profile(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieves personal loan profile data."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    if not app.employment_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personal loan profile not found")
    return success_response(PersonalLoanProfileRead.model_validate(app.employment_profile).model_dump())
