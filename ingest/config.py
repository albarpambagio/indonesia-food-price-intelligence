from datetime import datetime, timezone
from typing import Any

import duckdb

DB_PATH = "data/wfp.duckdb"
RAW_DATA_DIR = "data/raw"

FOOD_PRICES_CSV = f"{RAW_DATA_DIR}/wfp_food_prices_idn.csv"
MARKETS_CSV = f"{RAW_DATA_DIR}/wfp_markets_idn.csv"

LINEAGE_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS pipeline.lineage (
    run_id              TEXT PRIMARY KEY,
    started_at          TIMESTAMP,
    completed_at        TIMESTAMP,
    ingest_status       TEXT DEFAULT 'pending',
    transform_status    TEXT DEFAULT 'pending',
    forecast_status     TEXT DEFAULT 'pending',
    export_status       TEXT DEFAULT 'pending',
    raw_food_prices_rows INT,
    raw_markets_rows    INT,
    issues_log          JSONB
);
"""


def generate_run_id() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("pipeline_%Y%m%d_%H%M%S")


def get_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(DB_PATH, read_only=read_only)
    conn.execute("CREATE SCHEMA IF NOT EXISTS pipeline;")
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    conn.execute(LINEAGE_TABLE_DDL)
    return conn


def init_lineage(conn: duckdb.DuckDBPyConnection, run_id: str) -> None:
    conn.execute(
        """
        INSERT INTO pipeline.lineage (run_id, started_at, ingest_status)
        VALUES (?, CURRENT_TIMESTAMP, 'running')
        """,
        [run_id],
    )


def update_lineage(
    conn: duckdb.DuckDBPyConnection,
    run_id: str,
    **kwargs: Any,
) -> None:
    sets = ", ".join(f"{k.replace('_', ' ')} = ?" for k in kwargs)
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
            ingest_status = ?
        WHERE run_id = ?
        """,
        [status, run_id],
    )
