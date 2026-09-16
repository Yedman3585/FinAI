from fastapi import APIRouter, HTTPException, status

from app.domain.models import PaperPosition, PaperPositionCreate, PortfolioSummary
from app.market.registry import get_provider
from app.storage.database import create_paper_position, delete_position, list_position_rows, row_to_position

router = APIRouter()


@router.post("/positions", response_model=PaperPosition, status_code=status.HTTP_201_CREATED)
async def open_position(payload: PaperPositionCreate) -> PaperPosition:
    try:
        market = await get_provider(payload.provider).snapshot(payload.symbol)
        return create_paper_position(payload, market)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/positions", response_model=PortfolioSummary)
async def list_positions() -> PortfolioSummary:
    rows = list_position_rows()
    positions: list[PaperPosition] = []

    for row in rows:
        try:
            market = await get_provider(row["provider"]).snapshot(row["symbol"])
        except Exception:
            market = None
        positions.append(row_to_position(row, market))

    entry_value = round(sum(item.amount for item in positions), 2)
    current_value = round(sum(item.current_value for item in positions), 2)
    weighted_percent = (
        round((current_value - entry_value) / entry_value * 100, 2) if entry_value else 0
    )

    return PortfolioSummary(
        positions=positions,
        total_entry_value=entry_value,
        total_current_value=current_value,
        weighted_unrealized_percent=weighted_percent,
        note="Paper portfolio only: tracks learning experiments without sending broker orders.",
    )


@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
def close_position(position_id: str) -> None:
    if not delete_position(position_id):
        raise HTTPException(status_code=404, detail="Open paper position not found")
