from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from backend.loan_agency.schemas import LoanProductEnum, RuleOutcomeEnum


class RuleEngine:
    """
    Deterministic rule-based underwriting engine for Indian retail and SME lending.
    """

    @classmethod
    def evaluate(
        cls,
        loan_type: LoanProductEnum,
        requested_amount: Decimal,
        tenure_months: int,
        applicant_data: Dict[str, Any],
        profile_data: Dict[str, Any],
        foir_after: Decimal,
        ltv_percentage: Optional[Decimal] = None,
        uploaded_doc_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        triggered_rules: List[str] = []
        reason_codes: List[str] = []
        missing_fields: List[str] = []
        strengths: List[str] = []
        risk_factors: List[str] = []

        is_declined = False
        is_referred = False
        is_data_required = False

        current_year = datetime.now(timezone.utc).year
        docs = uploaded_doc_types or []

        # -------------------------------------------------------------
        # 1. KYC and Applicant Base Checks
        # -------------------------------------------------------------
        if not applicant_data.get("pan_masked") and not applicant_data.get("pan"):
            missing_fields.append("applicant.pan")
            is_data_required = True

        dob_str = applicant_data.get("date_of_birth")
        if dob_str:
            try:
                birth_year = int(dob_str.split("-")[0])
                age = current_year - birth_year
                if age < 21:
                    triggered_rules.append("R-AGE-01: Minimum age requirement is 21")
                    reason_codes.append("AGE_BELOW_MIN")
                    is_declined = True
                elif age > 65:
                    triggered_rules.append("R-AGE-02: Maximum applicant age is 65 at loan maturity")
                    reason_codes.append("AGE_EXCEEDS_MAX")
                    is_referred = True
                else:
                    strengths.append(f"Applicant age ({age} years) is within prime eligible band")
            except Exception:
                pass

        # -------------------------------------------------------------
        # 2. Credit History / CIBIL Checks
        # -------------------------------------------------------------
        cibil = profile_data.get("cibil_score", 750)
        has_write_offs = profile_data.get("has_write_offs", False)
        has_settlements = profile_data.get("has_settlements", False)
        has_overdues = profile_data.get("has_overdues", False)

        if has_write_offs or has_settlements:
            triggered_rules.append("R-CRED-01: Past write-offs or settlements detected on credit report")
            reason_codes.append("DEROGATORY_CREDIT_HISTORY")
            risk_factors.append("Applicant report has recorded write-offs or loan settlements")
            is_declined = True
        elif has_overdues:
            triggered_rules.append("R-CRED-02: Active overdue amounts reported")
            reason_codes.append("ACTIVE_OVERDUES")
            risk_factors.append("Active overdue balance requires clearing or manual justification")
            is_referred = True

        if cibil >= 750:
            strengths.append(f"Strong CIBIL bureau score ({cibil})")
        elif 650 <= cibil < 750:
            triggered_rules.append(f"R-CRED-03: CIBIL score ({cibil}) is in moderate band (650-749)")
            reason_codes.append("MODERATE_CIBIL_SCORE")
            risk_factors.append("CIBIL score is below prime threshold of 750")
            is_referred = True
        else:
            triggered_rules.append(f"R-CRED-04: CIBIL score ({cibil}) is below acceptable cutoff (<650)")
            reason_codes.append("LOW_CIBIL_SCORE")
            risk_factors.append("CIBIL score indicates high credit risk")
            is_declined = True

        # -------------------------------------------------------------
        # 3. Capacity & FOIR Checks
        # -------------------------------------------------------------
        if foir_after <= Decimal("50.0"):
            strengths.append(f"Healthy debt obligation ratio (FOIR: {foir_after}%)")
        elif Decimal("50.0") < foir_after <= Decimal("65.0"):
            triggered_rules.append(f"R-FOIR-01: Proposed FOIR ({foir_after}%) is moderately stretched")
            reason_codes.append("STRETCHED_FOIR")
            risk_factors.append(f"Proposed FOIR {foir_after}% is above conservative 50% benchmark")
            is_referred = True
        else:
            triggered_rules.append(f"R-FOIR-02: Proposed FOIR ({foir_after}%) exceeds maximum limit (>65%)")
            reason_codes.append("FOIR_EXCEEDED")
            risk_factors.append(f"Debt obligations of {foir_after}% exceed maximum debt service capacity")
            is_declined = True

        # -------------------------------------------------------------
        # 4. Product-Specific Policies
        # -------------------------------------------------------------
        if loan_type == LoanProductEnum.BUSINESS_LOAN:
            # Vintage
            start_year = profile_data.get("business_starting_year", current_year)
            vintage = current_year - start_year
            if vintage < 2:
                triggered_rules.append("R-BUS-01: Business vintage is less than 2 years")
                reason_codes.append("INSUFFICIENT_BUSINESS_VINTAGE")
                risk_factors.append(f"Business operational vintage is only {vintage} year(s)")
                is_referred = True
            else:
                strengths.append(f"Stable business operational track record ({vintage} years)")

            # Turnover
            turnover = Decimal(str(profile_data.get("previous_year_turnover", "0.0")))
            if turnover < Decimal("2000000.0"):  # 20 Lakhs min
                triggered_rules.append("R-BUS-02: Annual turnover is below 20 Lakhs minimum benchmark")
                reason_codes.append("LOW_ANNUAL_TURNOVER")
                risk_factors.append("Annual business turnover below ₹20L threshold")
                is_referred = True
            else:
                strengths.append(f"Robust declared turnover of ₹{turnover:,.2f}")

            # Bounces
            bounces = profile_data.get("cheque_emi_bounces_last_6m", 0)
            if bounces > 2:
                triggered_rules.append(f"R-BANK-01: Banking reflects {bounces} cheque/EMI bounces in last 6 months")
                reason_codes.append("FREQUENT_BANKING_BOUNCES")
                risk_factors.append(f"{bounces} banking return / inward bounce instances in statement")
                is_declined = True

            # Required docs
            required_docs = ["PAN", "GST_RETURNS", "BANK_STATEMENTS"]
            for req in required_docs:
                if not any(req in d for d in docs):
                    missing_fields.append(f"document.{req}")
                    is_data_required = True

        elif loan_type == LoanProductEnum.PERSONAL_LOAN:
            net_salary = Decimal(str(profile_data.get("net_salary_monthly", "0.0")))
            if net_salary < Decimal("25000.0"):
                triggered_rules.append("R-PL-01: Net monthly salary is below ₹25,000 minimum threshold")
                reason_codes.append("SALARY_BELOW_MINIMUM")
                risk_factors.append("Applicant net salary is below prime lending threshold")
                is_declined = True
            else:
                strengths.append(f"Steady salaried income of ₹{net_salary:,.2f}/month")

            exp = Decimal(str(profile_data.get("total_work_experience_years", "0.0")))
            if exp < Decimal("1.0"):
                triggered_rules.append("R-PL-02: Total work experience is less than 1 year")
                reason_codes.append("LOW_TOTAL_EXPERIENCE")
                is_referred = True

            # Required docs
            required_docs = ["PAN", "SALARY_SLIPS", "BANK_STATEMENTS"]
            for req in required_docs:
                if not any(req in d for d in docs):
                    missing_fields.append(f"document.{req}")
                    is_data_required = True

        elif loan_type == LoanProductEnum.USED_CAR_LOAN:
            mfg_year = profile_data.get("manufacturing_year", current_year)
            vehicle_age = current_year - mfg_year
            if vehicle_age > 10:
                triggered_rules.append(f"R-CAR-01: Vehicle age ({vehicle_age} yrs) exceeds 10-year policy limit")
                reason_codes.append("VEHICLE_TOO_OLD")
                risk_factors.append("Vehicle age exceeds maximum lender age limit of 10 years")
                is_declined = True

            if ltv_percentage is not None:
                if ltv_percentage > Decimal("95.0"):
                    triggered_rules.append(f"R-LTV-01: LTV ({ltv_percentage}%) exceeds maximum ceiling of 95%")
                    reason_codes.append("LTV_EXCEEDED")
                    risk_factors.append(f"Requested loan represents {ltv_percentage}% of vehicle value")
                    is_declined = True
                elif ltv_percentage > Decimal("85.0"):
                    triggered_rules.append(f"R-LTV-02: LTV ({ltv_percentage}%) is in high range (85-95%)")
                    reason_codes.append("HIGH_LTV")
                    is_referred = True
                else:
                    strengths.append(f"Conservative loan-to-value ratio ({ltv_percentage}%)")

            # Required docs
            required_docs = ["PAN", "RC", "BANK_STATEMENTS"]
            for req in required_docs:
                if not any(req in d for d in docs):
                    missing_fields.append(f"document.{req}")
                    is_data_required = True

        # -------------------------------------------------------------
        # Determine Final Outcome Hierarchy:
        # DECLINE > DATA_REQUIRED > REFER > PASS
        # -------------------------------------------------------------
        if is_declined:
            outcome = RuleOutcomeEnum.DECLINE
        elif is_data_required:
            outcome = RuleOutcomeEnum.DATA_REQUIRED
        elif is_referred:
            outcome = RuleOutcomeEnum.REFER
        else:
            outcome = RuleOutcomeEnum.PASS

        return {
            "outcome": outcome,
            "triggered_rules": triggered_rules,
            "reason_codes": reason_codes,
            "missing_fields": missing_fields,
            "strengths": strengths,
            "risk_factors": risk_factors,
        }
