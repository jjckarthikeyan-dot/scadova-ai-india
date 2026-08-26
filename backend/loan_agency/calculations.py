from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


def quantize_amount(value: Decimal) -> Decimal:
    """Quantizes a Decimal to 2 decimal places using standard ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_emi(
    principal: Decimal,
    annual_interest_rate: Decimal,
    tenure_months: int,
) -> Decimal:
    """
    Calculates monthly EMI using standard formula:
    EMI = [P x R x (1+R)^N] / [(1+R)^N - 1]
    where R = annual_rate / 12 / 100
    """
    if principal <= Decimal("0") or tenure_months <= 0:
        return Decimal("0.00")
    if annual_interest_rate <= Decimal("0"):
        return quantize_amount(principal / Decimal(tenure_months))

    monthly_rate = (annual_interest_rate / Decimal("100")) / Decimal("12")
    # Convert to float temporarily for power calculation to avoid decimal precision limits, then back to Decimal
    r_float = float(monthly_rate)
    n = tenure_months
    factor = (1.0 + r_float) ** n

    if factor == 1.0:
        return quantize_amount(principal / Decimal(tenure_months))

    emi_float = float(principal) * (r_float * factor) / (factor - 1.0)
    return quantize_amount(Decimal(str(emi_float)))


def calculate_foir(
    existing_emi: Decimal,
    monthly_income: Decimal,
    proposed_emi: Decimal = Decimal("0.0"),
) -> Decimal:
    """
    Calculates Fixed Obligation to Income Ratio (FOIR) percentage.
    FOIR = (Total EMI obligations / Net Monthly Income) * 100
    """
    if monthly_income <= Decimal("0"):
        return Decimal("100.00") if (existing_emi + proposed_emi) > Decimal("0") else Decimal("0.00")

    total_obligations = existing_emi + proposed_emi
    foir = (total_obligations / monthly_income) * Decimal("100")
    return quantize_amount(foir)


def calculate_max_affordable_emi(
    monthly_income: Decimal,
    existing_emi: Decimal,
    max_foir_percentage: Decimal = Decimal("50.0"),
) -> Decimal:
    """
    Calculates maximum affordable new EMI based on income and allowed FOIR threshold.
    Max Affordable EMI = (Income * Max FOIR %) - Existing EMI
    """
    if monthly_income <= Decimal("0"):
        return Decimal("0.00")

    max_total_emi = monthly_income * (max_foir_percentage / Decimal("100"))
    affordable_emi = max_total_emi - existing_emi
    return quantize_amount(max(Decimal("0.00"), affordable_emi))


def calculate_indicative_principal(
    max_emi: Decimal,
    annual_interest_rate: Decimal,
    tenure_months: int,
) -> Decimal:
    """
    Reverses the EMI formula to estimate maximum loan principal from affordable EMI.
    P = EMI * [(1+R)^N - 1] / [R * (1+R)^N]
    """
    if max_emi <= Decimal("0") or tenure_months <= 0:
        return Decimal("0.00")
    if annual_interest_rate <= Decimal("0"):
        return quantize_amount(max_emi * Decimal(tenure_months))

    monthly_rate = (annual_interest_rate / Decimal("100")) / Decimal("12")
    r_float = float(monthly_rate)
    n = tenure_months
    factor = (1.0 + r_float) ** n

    if factor == 1.0 or r_float == 0:
        return quantize_amount(max_emi * Decimal(tenure_months))

    principal_float = float(max_emi) * (factor - 1.0) / (r_float * factor)
    return quantize_amount(Decimal(str(principal_float)))


def calculate_ltv(
    loan_amount: Decimal,
    asset_valuation: Decimal,
) -> Decimal:
    """
    Calculates Loan to Value (LTV) percentage.
    LTV = (Loan Amount / Valuation) * 100
    """
    if asset_valuation <= Decimal("0"):
        return Decimal("0.00")
    ltv = (loan_amount / asset_valuation) * Decimal("100")
    return quantize_amount(ltv)


def calculate_required_down_payment(
    purchase_price: Decimal,
    approved_loan_amount: Decimal,
) -> Decimal:
    """
    Calculates down payment required from borrower.
    Down Payment = Purchase Price - Approved Loan Amount
    """
    return quantize_amount(max(Decimal("0.00"), purchase_price - approved_loan_amount))
