from typing import Optional

from fastapi import APIRouter

from app.domain.finance import summarize_profile
from app.domain.models import FinancialProfileRequest, FinancialProfileSummary, StoredProfileSnapshot
from app.storage.database import get_latest_profile, save_profile_snapshot

router = APIRouter()


@router.post("/profile", response_model=FinancialProfileSummary)
def profile_summary(payload: FinancialProfileRequest) -> FinancialProfileSummary:
    summary = summarize_profile(payload)
    save_profile_snapshot(payload, summary)
    return summary


@router.get("/profile/latest", response_model=Optional[StoredProfileSnapshot])
def latest_profile() -> Optional[dict]:
    return get_latest_profile()
