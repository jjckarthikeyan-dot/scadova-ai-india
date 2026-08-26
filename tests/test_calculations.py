from decimal import Decimal
from backend.loan_agency.calculations import (
    calculate_emi,
    calculate_foir,
    calculate_indicative_principal,
    calculate_ltv,
    calculate_max_affordable_emi,
    calculate_required_down_payment,
)


def test_calculate_emi():
    # 10 Lakhs at 12% for 24 months
    # Formula check: Standard EMI for 1,000,000 at 1% monthly for 24 mos is ~ 47,073.47
    principal = Decimal("1000000.00")
    rate = Decimal("12.0")
    tenure = 24

    emi = calculate_emi(principal, rate, tenure)
    assert isinstance(emi, Decimal)
    assert emi == Decimal("47073.47")

    # Edge cases
    assert calculate_emi(Decimal("0.0"), rate, tenure) == Decimal("0.00")
    assert calculate_emi(principal, Decimal("0.0"), 10) == Decimal("100000.00")


def test_calculate_foir():
    # Monthly Income: 100,000, Existing EMI: 20,000, Proposed EMI: 30,000
    income = Decimal("100000.00")
    existing_emi = Decimal("20000.00")
    proposed_emi = Decimal("30000.00")

    foir_current = calculate_foir(existing_emi, income)
    assert foir_current == Decimal("20.00")

    foir_after = calculate_foir(existing_emi, income, proposed_emi)
    assert foir_after == Decimal("50.00")

    # Zero income edge case
    assert calculate_foir(existing_emi, Decimal("0.0")) == Decimal("100.00")


def test_calculate_max_affordable_emi():
    # Income: 80,000, Existing: 15,000, Max FOIR: 50% (Limit = 40,000)
    income = Decimal("80000.00")
    existing = Decimal("15000.00")
    max_emi = calculate_max_affordable_emi(income, existing, Decimal("50.0"))
    assert max_emi == Decimal("25000.00")


def test_calculate_indicative_principal():
    # Max EMI = 25,000, Rate = 12%, Tenure = 24 months -> Estimated Principal ~ 531,080.82
    emi = Decimal("25000.00")
    principal = calculate_indicative_principal(emi, Decimal("12.0"), 24)
    assert principal > Decimal("500000.00")
    assert isinstance(principal, Decimal)


def test_calculate_ltv():
    loan_amount = Decimal("800000.00")
    valuation = Decimal("1000000.00")
    ltv = calculate_ltv(loan_amount, valuation)
    assert ltv == Decimal("80.00")


def test_calculate_required_down_payment():
    purchase_price = Decimal("950000.00")
    approved_loan = Decimal("800000.00")
    dp = calculate_required_down_payment(purchase_price, approved_loan)
    assert dp == Decimal("150000.00")
