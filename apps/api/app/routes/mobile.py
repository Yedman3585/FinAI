from fastapi import APIRouter, HTTPException

from app.domain.models import MobileSessionRequest, MobileSessionResponse
from app.mobile.session import build_mobile_session
from app.storage.database import save_analysis_review, save_deep_analysis_run

router = APIRouter()


@router.post("/session", response_model=MobileSessionResponse)
async def mobile_session(payload: MobileSessionRequest) -> MobileSessionResponse:
    try:
        session = await build_mobile_session(payload)
        save_deep_analysis_run(session.analysis)
        if session.review is not None:
            save_analysis_review(session.review)
        return session
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
