"""
Heart Digital Twin — FastAPI Backend
=====================================
Entry point for the backend API.

Run with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

From the project root (Heart New/).
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.model_loader import model_service
from backend.routes.health import router as health_router
from backend.routes.predict import router as predict_router
from backend.routes.simulate import router as simulate_router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan: load model at startup, clean up at shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    LOGGER.info("🫀 Digital Twin of the Heart — starting up …")
    try:
        model_service.load()
        LOGGER.info("✅ Ensemble model loaded and ready.")
    except Exception as exc:
        LOGGER.error("❌ Failed to load model: %s", exc)
        # Allow server to start without model; /health will report model_loaded=False
    yield
    LOGGER.info("🛑 Shutting down Digital Twin backend …")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Digital Twin of the Heart",
    description="""
## 🫀 Heart Disease Risk Prediction API

A production-ready AI backend that combines three trained cardiovascular models
(Cardio, Framingham, UCI) into an ensemble for heart risk assessment.

### Key Endpoints
- **GET /health** — Liveness check
- **POST /predict** — Full heart risk prediction with SHAP explanations
- **POST /simulate** — Digital twin what-if scenario simulation

### Risk Score
The `HeartRiskScore` (0–100) is derived from the mean ensemble probability:
- **0–39**: Low risk
- **40–69**: Moderate risk
- **70–100**: High risk
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---------------------------------------------------------------------------
# CORS — allow all origins in development, restrict in production
# ---------------------------------------------------------------------------

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://heart-new-beta.vercel.app",                 # Your main production URL
        "https://heart-new-git-main-om-more.vercel.app",      # Git branch URL
        "http://localhost:5173"                               # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health_router)
app.include_router(predict_router)
app.include_router(simulate_router)


# ---------------------------------------------------------------------------
# Root redirect to docs
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "message": "Digital Twin of the Heart API",
            "docs": "/docs",
            "health": "/health",
        }
    )
