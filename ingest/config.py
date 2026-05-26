from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "wfp.duckdb")
RAW_DATA_DIR = str(PROJECT_ROOT / "data" / "raw")

FOOD_PRICES_CSV = f"{RAW_DATA_DIR}/wfp_food_prices_idn.csv"
MARKETS_CSV = f"{RAW_DATA_DIR}/wfp_markets_idn.csv"

LINEAGE_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS pipeline.lineage (
    run_id              TEXT PRIMARY KEY,
    started_at          TIMESTAMP,
    completed_at        TIMESTAMP,
    pipeline_status     TEXT DEFAULT 'pending',
    ingest_status       TEXT DEFAULT 'pending',
    transform_status    TEXT DEFAULT 'pending',
    forecast_status     TEXT DEFAULT 'pending',
    export_status       TEXT DEFAULT 'pending',
    raw_food_prices_rows INT,
    raw_markets_rows    INT,
    issues_log          JSON
);
"""


def generate_run_id() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("pipeline_%Y%m%d_%H%M%S")


def ensure_lineage_table(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("CREATE SCHEMA IF NOT EXISTS pipeline;")
    conn.execute(LINEAGE_TABLE_DDL)


def get_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(DB_PATH, read_only=read_only)
    ensure_lineage_table(conn)
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    return conn


def init_lineage(conn: duckdb.DuckDBPyConnection, run_id: str) -> None:
    conn.execute(
        """
        INSERT INTO pipeline.lineage (run_id, started_at, pipeline_status)
        VALUES (?, CURRENT_TIMESTAMP, 'running')
        """,
        [run_id],
    )


def update_lineage(
    conn: duckdb.DuckDBPyConnection,
    run_id: str,
    **kwargs: Any,
) -> None:
    sets = ", ".join(f'"{k}" = ?' for k in kwargs)
    if not sets:
        return
    values = list(kwargs.values())
    conn.execute(f"UPDATE pipeline.lineage SET {sets} WHERE run_id = ?", [*values, run_id])


def complete_lineage(
    conn: duckdb.DuckDBPyConnection,
    run_id: str,
    status: str = "completed",
) -> None:
    conn.execute(
        """
        UPDATE pipeline.lineage
        SET completed_at = CURRENT_TIMESTAMP,
            pipeline_status = ?
        WHERE run_id = ?
        """,
        [status, run_id],
    )
