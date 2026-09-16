from fastapi import APIRouter, HTTPException

from app.agents.deep_analysis import (
    build_deep_analysis,
    build_opportunity_radar,
    render_deep_analysis_markdown,
)
from app.agents.external_engines import list_external_engines
from app.agents.mandates import list_mandates
from app.agents.prompt_library import list_prompt_templates
from app.agents.review import build_analysis_review
from app.domain.models import (
    AgentPromptTemplate,
    AnalysisReviewResponse,
    AnalysisReviewSummary,
    AgentMandate,
    DeepAnalysisRequest,
    DeepAnalysisResponse,
    DeepAnalysisRunSummary,
    ExternalEngineStatus,
    OpportunityRadarRequest,
    OpportunityRadarResponse,
    RenderedMemo,
)
from app.storage.database import (
    get_deep_analysis_run,
    list_analysis_reviews,
    list_deep_analysis_runs,
    save_analysis_review,
    save_deep_analysis_run,
)

router = APIRouter()


@router.get("/engines", response_model=list[ExternalEngineStatus])
def engines() -> list[ExternalEngineStatus]:
    return list_external_engines()


@router.get("/prompts", response_model=list[AgentPromptTemplate])
def prompts() -> list[AgentPromptTemplate]:
    return list_prompt_templates()


@router.get("/mandates", response_model=list[AgentMandate])
def mandates() -> list[AgentMandate]:
    return list_mandates()


@router.post("/deep-analysis", response_model=DeepAnalysisResponse)
async def deep_analysis(payload: DeepAnalysisRequest) -> DeepAnalysisResponse:
    try:
        analysis = await build_deep_analysis(payload)
        save_deep_analysis_run(analysis)
        return analysis
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/opportunity-radar", response_model=OpportunityRadarResponse)
async def opportunity_radar(payload: OpportunityRadarRequest) -> OpportunityRadarResponse:
    try:
        return await build_opportunity_radar(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/runs", response_model=list[DeepAnalysisRunSummary])
def analysis_runs(limit: int = 20) -> list[DeepAnalysisRunSummary]:
    return list_deep_analysis_runs(limit=min(max(limit, 1), 100))


@router.get("/reviews", response_model=list[AnalysisReviewSummary])
def analysis_reviews(limit: int = 20) -> list[AnalysisReviewSummary]:
    return list_analysis_reviews(limit=min(max(limit, 1), 100))


@router.get("/runs/{run_id}/review", response_model=AnalysisReviewResponse)
async def analysis_run_review(run_id: str) -> AnalysisReviewResponse:
    raw = get_deep_analysis_run(run_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="Deep analysis run not found")
    try:
        analysis = DeepAnalysisResponse.model_validate(raw)
        review = await build_analysis_review(analysis)
        save_analysis_review(review)
        return review
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/runs/{run_id}", response_model=DeepAnalysisResponse)
def analysis_run(run_id: str) -> dict:
    analysis = get_deep_analysis_run(run_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Deep analysis run not found")
    return analysis


@router.get("/runs/{run_id}/memo", response_model=RenderedMemo)
def analysis_run_memo(run_id: str) -> RenderedMemo:
    raw = get_deep_analysis_run(run_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="Deep analysis run not found")
    analysis = DeepAnalysisResponse.model_validate(raw)
    return RenderedMemo(id=analysis.id, markdown=render_deep_analysis_markdown(analysis))
