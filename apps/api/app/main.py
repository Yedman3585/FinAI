from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.agents import router as agents_router
from app.routes.finance import router as finance_router
from app.routes.markets import router as markets_router
from app.routes.mobile import router as mobile_router
from app.routes.portfolio import router as portfolio_router
from app.routes.scenarios import router as scenarios_router
from app.storage.database import init_db


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Personal finance and investment decision API for FInAI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(finance_router, prefix="/api/finance", tags=["finance"])
app.include_router(markets_router, prefix="/api/markets", tags=["markets"])
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(scenarios_router, prefix="/api/scenarios", tags=["scenarios"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(mobile_router, prefix="/api/mobile", tags=["mobile"])


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
