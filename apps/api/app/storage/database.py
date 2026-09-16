from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from app.core.config import settings
from app.domain.models import (
    AnalysisReviewResponse,
    AnalysisReviewSummary,
    Currency,
    DeepAnalysisResponse,
    DeepAnalysisRunSummary,
    FinancialProfileRequest,
    FinancialProfileSummary,
    MarketSnapshot,
    PaperPosition,
    PaperPositionCreate,
)


def _db_path() -> Path:
    path = Path(settings.sqlite_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(_db_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS profile_snapshots (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                request_json TEXT NOT NULL,
                summary_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_positions (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                provider TEXT NOT NULL,
                exchange TEXT NOT NULL,
                currency TEXT NOT NULL,
                amount REAL NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                thesis TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS deep_analysis_runs (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                symbol TEXT NOT NULL,
                provider TEXT NOT NULL,
                action TEXT NOT NULL,
                conviction_score REAL NOT NULL,
                risk_score REAL NOT NULL,
                response_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_reviews (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                reviewed_at TEXT NOT NULL,
                symbol TEXT NOT NULL,
                provider TEXT NOT NULL,
                thesis_status TEXT NOT NULL,
                return_percent REAL NOT NULL,
                review_json TEXT NOT NULL
            )
            """
        )


def save_profile_snapshot(
    request: FinancialProfileRequest,
    summary: FinancialProfileSummary,
) -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO profile_snapshots (id, created_at, request_json, summary_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                now,
                request.model_dump_json(),
                summary.model_dump_json(),
            ),
        )


def get_latest_profile() -> Optional[dict[str, Any]]:
    init_db()
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT created_at, request_json, summary_json
            FROM profile_snapshots
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()

    if row is None:
        return None

    return {
        "created_at": row["created_at"],
        "request": json.loads(row["request_json"]),
        "summary": json.loads(row["summary_json"]),
    }


def create_paper_position(
    payload: PaperPositionCreate,
    market: MarketSnapshot,
) -> PaperPosition:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    position_id = str(uuid4())
    quantity = round(payload.amount / market.last_price, 8) if market.last_price else 0

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO paper_positions (
                id, symbol, provider, exchange, currency, amount, quantity,
                entry_price, thesis, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                position_id,
                market.symbol,
                market.provider,
                market.exchange,
                market.currency.value,
                payload.amount,
                quantity,
                market.last_price,
                payload.thesis,
                "open",
                now,
            ),
        )

    return PaperPosition(
        id=position_id,
        symbol=market.symbol,
        provider=market.provider,
        exchange=market.exchange,
        currency=market.currency,
        amount=round(payload.amount, 2),
        quantity=quantity,
        entry_price=market.last_price,
        current_price=market.last_price,
        current_value=round(quantity * market.last_price, 2),
        unrealized_percent=0,
        status="open",
        thesis=payload.thesis,
        created_at=now,
        source_note=market.source_note,
    )


def list_position_rows() -> list[sqlite3.Row]:
    init_db()
    with _connect() as connection:
        return connection.execute(
            """
            SELECT id, symbol, provider, exchange, currency, amount, quantity,
                   entry_price, thesis, status, created_at
            FROM paper_positions
            WHERE status = 'open'
            ORDER BY created_at DESC
            """
        ).fetchall()


def delete_position(position_id: str) -> bool:
    init_db()
    with _connect() as connection:
        cursor = connection.execute(
            "UPDATE paper_positions SET status = 'closed' WHERE id = ? AND status = 'open'",
            (position_id,),
        )
        return cursor.rowcount > 0


def row_to_position(row: sqlite3.Row, market: Optional[MarketSnapshot] = None) -> PaperPosition:
    current_price = market.last_price if market is not None else float(row["entry_price"])
    quantity = float(row["quantity"])
    entry_value = float(row["amount"])
    current_value = round(quantity * current_price, 2)
    unrealized_percent = (
        round((current_value - entry_value) / entry_value * 100, 2) if entry_value else 0
    )

    return PaperPosition(
        id=row["id"],
        symbol=row["symbol"],
        provider=row["provider"],
        exchange=market.exchange if market is not None else row["exchange"],
        currency=Currency(market.currency.value if market is not None else row["currency"]),
        amount=round(entry_value, 2),
        quantity=round(quantity, 8),
        entry_price=round(float(row["entry_price"]), 4),
        current_price=round(current_price, 4),
        current_value=current_value,
        unrealized_percent=unrealized_percent,
        status=row["status"],
        thesis=row["thesis"],
        created_at=row["created_at"],
        source_note=market.source_note if market is not None else "Using stored entry price fallback.",
    )


def save_deep_analysis_run(analysis: DeepAnalysisResponse) -> None:
    init_db()
    with _connect() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO deep_analysis_runs (
                id, created_at, symbol, provider, action,
                conviction_score, risk_score, response_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis.id,
                analysis.created_at,
                analysis.market.symbol,
                analysis.market.provider,
                analysis.memo.action,
                analysis.memo.conviction_score,
                analysis.memo.risk_score,
                analysis.model_dump_json(),
            ),
        )


def list_deep_analysis_runs(limit: int = 20) -> list[DeepAnalysisRunSummary]:
    init_db()
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, symbol, provider, action, conviction_score, risk_score
            FROM deep_analysis_runs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        DeepAnalysisRunSummary(
            id=row["id"],
            created_at=row["created_at"],
            symbol=row["symbol"],
            provider=row["provider"],
            action=row["action"],
            conviction_score=round(float(row["conviction_score"]), 2),
            risk_score=round(float(row["risk_score"]), 2),
        )
        for row in rows
    ]


def get_deep_analysis_run(run_id: str) -> Optional[dict[str, Any]]:
    init_db()
    with _connect() as connection:
        row = connection.execute(
            "SELECT response_json FROM deep_analysis_runs WHERE id = ?",
            (run_id,),
        ).fetchone()

    if row is None:
        return None
    return json.loads(row["response_json"])


def save_analysis_review(review: AnalysisReviewResponse) -> None:
    init_db()
    with _connect() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO analysis_reviews (
                id, run_id, reviewed_at, symbol, provider,
                thesis_status, return_percent, review_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review.id,
                review.run_id,
                review.reviewed_at,
                review.symbol,
                review.provider,
                review.thesis_status,
                review.return_percent,
                review.model_dump_json(),
            ),
        )


def list_analysis_reviews(limit: int = 20) -> list[AnalysisReviewSummary]:
    init_db()
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, run_id, reviewed_at, symbol, provider, thesis_status, return_percent
            FROM analysis_reviews
            ORDER BY reviewed_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        AnalysisReviewSummary(
            id=row["id"],
            run_id=row["run_id"],
            reviewed_at=row["reviewed_at"],
            symbol=row["symbol"],
            provider=row["provider"],
            thesis_status=row["thesis_status"],
            return_percent=round(float(row["return_percent"]), 2),
        )
        for row in rows
    ]
