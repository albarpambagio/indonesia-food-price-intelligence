import json
import logging
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingest.config import LINEAGE_TABLE_DDL, ensure_lineage_table

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "wfp.duckdb")
OUTPUT_DIR = PROJECT_ROOT / "dashboard" / "public" / "data"
LOG_DIR = PROJECT_ROOT / "logs"
SCHEMA = "wfp_marts"

MART_EXPORTS = [
    {
        "source": f"{SCHEMA}.mart_price_trends",
        "filename": "price_trends.json",
        "order_by": "month, commodity_consolidated, island_group, admin1",
    },
    {
        "source": f"{SCHEMA}.mart_seasonal_patterns",
        "filename": "seasonal_patterns.json",
        "order_by": "month, commodity_consolidated, island_group",
    },
    {
        "source": f"{SCHEMA}.mart_geo_disparity",
        "filename": "geographic_disparity.json",
        "order_by": "year, commodity_consolidated, island_group, admin1",
    },
    {
        "source": f"{SCHEMA}.mart_commodity_correlation",
        "filename": "commodity_correlation.json",
        "order_by": "month",
    },
    {
        "source": f"{SCHEMA}.mart_correlation_summary",
        "filename": "correlation_summary.json",
        "order_by": "commodity_pair, lag_months",
    },
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_DIR / "export.log")),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def export_table(conn: duckdb.DuckDBPyConnection, cfg: dict) -> int:
    source = cfg["source"]
    filename = cfg["filename"]
    order_by = cfg.get("order_by", "")

    query = f"SELECT * FROM {source}"
    if order_by:
        query += f" ORDER BY {order_by}"

    df = conn.execute(query).fetchdf()
    df = df.replace({np.nan: None, float("nan"): None, float("inf"): None, float("-inf"): None})
    records = df.to_dict(orient="records")

    output_path = OUTPUT_DIR / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str, allow_nan=False)

    row_count = len(records)
    logger.info("  %s -> %s (%d records)", source, filename, row_count)
    return row_count


def verify_export(conn: duckdb.DuckDBPyConnection, cfg: dict, exported_count: int) -> bool:
    source = cfg["source"]
    filename = cfg["filename"]
    db_count = conn.execute(f"SELECT COUNT(*) FROM {source}").fetchone()[0]
    if db_count != exported_count:
        logger.error(
            "  FAIL %s: DB has %d rows, exported %d rows",
            filename, db_count, exported_count,
        )
        return False
    logger.info("  OK %s: DB=%d exported=%d", filename, db_count, exported_count)
    return True


def update_lineage(conn: duckdb.DuckDBPyConnection, run_id: str, status: str, issues: list[str] | None = None) -> None:
    try:
        ensure_lineage_table(conn)
        conn.execute("""
            INSERT INTO pipeline.lineage (run_id, export_status, issues_log)
            VALUES (?, ?, ?::JSON)
            ON CONFLICT (run_id)
            DO UPDATE SET export_status = EXCLUDED.export_status,
                          issues_log = EXCLUDED.issues_log
        """, [run_id, status, json.dumps({"export_issues": issues or []})])
    except Exception as e:
        logger.warning("Could not update lineage: %s", e)


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else datetime.now(timezone.utc).strftime("pipeline_%Y%m%d_%H%M%S")
    logger.info("=" * 60)
    logger.info("Export run started | run_id=%s", run_id)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_passed = True
    issues: list[str] = []
    fcount = 0

    try:
        conn = duckdb.connect(DB_PATH)

        mart_counts: dict[str, int] = {}
        for cfg in MART_EXPORTS:
            exported = export_table(conn, cfg)
            mart_counts[cfg["filename"]] = exported
            ok = verify_export(conn, cfg, exported)
            if not ok:
                all_passed = False
                issues.append(f"Row count mismatch for {cfg['filename']}")

        forecast_src = OUTPUT_DIR / "forecast.json"
        if forecast_src.exists():
            with open(forecast_src, encoding="utf-8") as f:
                fdata = json.load(f)
            fcount = len(fdata.get("data", []))
            logger.info("  forecast.json -> copied (%d records)", fcount)
        else:
            logger.warning("  forecast.json not found — run forecast/run_forecast.py first")
            issues.append("forecast.json missing — run forecast first")

        status = "completed" if all_passed else "completed_with_warnings"
        update_lineage(conn, run_id, status, issues)
        conn.close()

        logger.info("Export run complete | status=%s | run_id=%s", status, run_id)
        logger.info("Mart row counts: %s", json.dumps(mart_counts))

        if not all_passed:
            sys.exit(1)

    except Exception as e:
        logger.exception("Export run failed: %s", e)
        try:
            conn2 = duckdb.connect(DB_PATH)
            update_lineage(conn2, run_id, "failed", [str(e)])
            conn2.close()
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
