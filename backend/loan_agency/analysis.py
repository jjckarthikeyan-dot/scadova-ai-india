from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.common.audit import log_audit_event
from backend.common.responses import success_response
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.loan_agency.repository import LoanAgencyRepository
from backend.loan_agency.schemas import AnalysisResponse, ApplicationStatusEnum, LoanProductEnum, RuleOutcomeEnum
from backend.loan_agency.service import LoanAgencyService

router = APIRouter()


@router.post("/{application_id}")
def run_loan_analysis(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Executes deterministic financial calculations and rule engine evaluation
    for an application, generating indicative eligibility, FOIR, EMI, and lender categorization.
    """
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")

    analysis_result = LoanAgencyService.execute_analysis(db, application_id)
    log_audit_event(
        db,
        event_type="ANALYSIS_EXECUTED",
        entity_type="analysis_run",
        entity_id=application_id,
        user_id=current_user.get("id"),
        details={
            "outcome": analysis_result["rule_outcome"].value,
            "eligible_amount": str(analysis_result["indicative_eligible_amount"]),
        },
    )
    return success_response(analysis_result)


@router.get("/{application_id}/latest")
def get_latest_loan_analysis(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieves the latest analysis report for a loan application."""
    app = LoanAgencyRepository.get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")

    latest_run = LoanAgencyRepository.get_latest_analysis_run(db, application_id)
    if not latest_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis runs found for this application. Run POST /api/loan-agency/analysis/{id} first.",
        )

    response_data = {
        "application_id": app.id,
        "application_number": app.application_number,
        "loan_type": LoanProductEnum(app.loan_type),
        "status": ApplicationStatusEnum(app.status),
        "rule_outcome": RuleOutcomeEnum(latest_run.rule_outcome),
        "indicative_eligible_amount": latest_run.eligible_amount,
        "calculated_emi": latest_run.calculated_emi,
        "foir_before_percentage": latest_run.foir_before,
        "foir_after_percentage": latest_run.foir_after,
        "ltv_percentage": latest_run.ltv_percentage,
        "recommended_lender_category": latest_run.recommended_lender_category,
        "strengths": latest_run.strengths or [],
        "risk_factors": latest_run.risk_factors or [],
        "missing_information": latest_run.missing_information or [],
        "rule_reason_codes": latest_run.rule_reason_codes or [],
        "ai_summary": latest_run.ai_summary,
        "disclaimer": latest_run.disclaimer,
        "timestamp": latest_run.created_at,
    }
    return success_response(response_data)
