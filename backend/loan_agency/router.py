from fastapi import APIRouter

from backend.loan_agency.analysis import router as analysis_router
from backend.loan_agency.applications import router as applications_router
from backend.loan_agency.business_loans import router as business_loans_router
from backend.loan_agency.documents import router as documents_router
from backend.loan_agency.personal_loans import router as personal_loans_router
from backend.loan_agency.used_car_loans import router as used_car_loans_router

router = APIRouter()

router.include_router(
    applications_router,
    prefix="/applications",
    tags=["Loan Applications"],
)

router.include_router(
    business_loans_router,
    prefix="/business-loans",
    tags=["Business Loans"],
)

router.include_router(
    personal_loans_router,
    prefix="/personal-loans",
    tags=["Personal Loans"],
)

router.include_router(
    used_car_loans_router,
    prefix="/used-car-loans",
    tags=["Used Car Loans"],
)

router.include_router(
    documents_router,
    prefix="/documents",
    tags=["Loan Documents"],
)

router.include_router(
    analysis_router,
    prefix="/analysis",
    tags=["Loan Analysis"],
)


@router.get("/")
async def loan_agency_home():
    return {
        "success": True,
        "module": "loan_agency",
        "status": "running",
        "products": [
            "business_loan",
            "personal_loan",
            "used_car_loan",
        ],
    }
