from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.common.audit import log_audit_event
from backend.common.responses import success_response
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.loan_agency.repository import LoanAgencyRepository
from backend.loan_agency.schemas import (
    LoanProductEnum,
    UsedCarLoanProfileRead,
    UsedCarLoanProfileUpdate,
)

router = APIRouter()


@router.put("/{application_id}")
def update_used_car_loan_profile(
    application_id: str,
    payload: UsedCarLoanProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Saves or updates used car loan profile data."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    if app.loan_type != LoanProductEnum.USED_CAR_LOAN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application {application_id} is for {app.loan_type}, not USED_CAR_LOAN",
        )

    profile = LoanAgencyRepository.save_vehicle_profile(db, application_id, payload)
    log_audit_event(
        db,
        event_type="VEHICLE_PROFILE_UPDATED",
        entity_type="vehicle_profile",
        entity_id=profile.id,
        user_id=current_user.get("id"),
        details=payload.model_dump(mode="json"),
    )
    return success_response(UsedCarLoanProfileRead.model_validate(profile).model_dump())


@router.get("/{application_id}")
def get_used_car_loan_profile(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieves used car loan profile data."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    if not app.vehicle_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle loan profile not found")
    return success_response(UsedCarLoanProfileRead.model_validate(app.vehicle_profile).model_dump())
