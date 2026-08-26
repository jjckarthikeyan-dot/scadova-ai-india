from decimal import Decimal
from backend.loan_agency.rules import RuleEngine
from backend.loan_agency.schemas import LoanProductEnum, RuleOutcomeEnum


def test_rule_engine_pass():
    applicant_data = {"pan_masked": "AB*****34F", "date_of_birth": "1990-05-15"}
    profile_data = {
        "cibil_score": 780,
        "has_write_offs": False,
        "has_settlements": False,
        "has_overdues": False,
        "net_salary_monthly": Decimal("75000.00"),
        "total_work_experience_years": Decimal("4.0"),
    }
    uploaded_docs = ["PAN", "SALARY_SLIPS", "BANK_STATEMENTS"]

    result = RuleEngine.evaluate(
        loan_type=LoanProductEnum.PERSONAL_LOAN,
        requested_amount=Decimal("300000.00"),
        tenure_months=24,
        applicant_data=applicant_data,
        profile_data=profile_data,
        foir_after=Decimal("35.00"),
        uploaded_doc_types=uploaded_docs,
    )

    assert result["outcome"] == RuleOutcomeEnum.PASS
    assert len(result["strengths"]) > 0
    assert len(result["missing_fields"]) == 0


def test_rule_engine_refer():
    applicant_data = {"pan_masked": "AB*****34F", "date_of_birth": "1990-05-15"}
    profile_data = {
        "cibil_score": 680,  # Moderate CIBIL -> REFER
        "has_write_offs": False,
        "has_settlements": False,
        "has_overdues": False,
        "net_salary_monthly": Decimal("60000.00"),
        "total_work_experience_years": Decimal("2.0"),
    }
    uploaded_docs = ["PAN", "SALARY_SLIPS", "BANK_STATEMENTS"]

    result = RuleEngine.evaluate(
        loan_type=LoanProductEnum.PERSONAL_LOAN,
        requested_amount=Decimal("300000.00"),
        tenure_months=24,
        applicant_data=applicant_data,
        profile_data=profile_data,
        foir_after=Decimal("45.00"),
        uploaded_doc_types=uploaded_docs,
    )

    assert result["outcome"] == RuleOutcomeEnum.REFER
    assert "MODERATE_CIBIL_SCORE" in result["reason_codes"]


def test_rule_engine_decline_write_offs():
    applicant_data = {"pan_masked": "AB*****34F", "date_of_birth": "1990-05-15"}
    profile_data = {
        "cibil_score": 780,
        "has_write_offs": True,  # Derogatory record -> DECLINE
        "has_settlements": False,
        "has_overdues": False,
        "net_salary_monthly": Decimal("80000.00"),
        "total_work_experience_years": Decimal("5.0"),
    }
    uploaded_docs = ["PAN", "SALARY_SLIPS", "BANK_STATEMENTS"]

    result = RuleEngine.evaluate(
        loan_type=LoanProductEnum.PERSONAL_LOAN,
        requested_amount=Decimal("500000.00"),
        tenure_months=36,
        applicant_data=applicant_data,
        profile_data=profile_data,
        foir_after=Decimal("40.00"),
        uploaded_doc_types=uploaded_docs,
    )

    assert result["outcome"] == RuleOutcomeEnum.DECLINE
    assert "DEROGATORY_CREDIT_HISTORY" in result["reason_codes"]


def test_rule_engine_data_required():
    # Missing required documents
    applicant_data = {"pan_masked": "AB*****34F", "date_of_birth": "1990-05-15"}
    profile_data = {
        "cibil_score": 760,
        "has_write_offs": False,
        "has_settlements": False,
        "has_overdues": False,
        "net_salary_monthly": Decimal("50000.00"),
        "total_work_experience_years": Decimal("3.0"),
    }
    uploaded_docs = []  # No docs uploaded

    result = RuleEngine.evaluate(
        loan_type=LoanProductEnum.PERSONAL_LOAN,
        requested_amount=Decimal("200000.00"),
        tenure_months=24,
        applicant_data=applicant_data,
        profile_data=profile_data,
        foir_after=Decimal("30.00"),
        uploaded_doc_types=uploaded_docs,
    )

    assert result["outcome"] == RuleOutcomeEnum.DATA_REQUIRED
    assert len(result["missing_fields"]) > 0
