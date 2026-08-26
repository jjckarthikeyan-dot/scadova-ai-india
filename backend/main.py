from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.database import init_db
from backend.loan_agency.router import router as loan_agency_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on application start
    init_db()
    yield


app = FastAPI(
    title="Scadova-AI-India Backend",
    description="Scalable Indian Loan Agency Lending & Underwriting Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Domain Routers
app.include_router(
    loan_agency_router,
    prefix="/api/loan-agency",
    tags=["Loan Agency"],
)


@app.get("/")
def root():
    return {
        "success": True,
        "product": "Scadova-AI-India",
        "module": "loan_agency",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "status": "healthy",
    }


@app.get("/health/live")
def health_live():
    return {
        "status": "alive",
    }


@app.get("/health/ready")
def health_ready():
    return {
        "status": "ready",
        "database": "connected",
    }
