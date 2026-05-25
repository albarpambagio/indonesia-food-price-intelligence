import logging
import sys
from pathlib import Path

from config import (
    FOOD_PRICES_CSV,
    MARKETS_CSV,
    generate_run_id,
    get_connection,
    init_lineage,
    update_lineage,
    complete_lineage,
)

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = str(LOG_DIR / "ingest.log")
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def count_csv_lines(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        line_count = sum(1 for _ in f)
    return line_count - 1


def load_csv_to_raw(
    conn,
    csv_path: str,
    table_name: str,
    run_id: str,
) -> int:
    logger.info("Loading %s -> raw.%s ...", csv_path, table_name)
    conn.execute(f"DROP TABLE IF EXISTS raw.{table_name}")
    conn.execute(f"CREATE TABLE raw.{table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")
    row_count = conn.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()[0]
    logger.info("Loaded %d rows into raw.%s", row_count, table_name)
    return row_count


def reconcile(
    conn,
    csv_path: str,
    table: str,
    run_id: str,
    label: str,
) -> None:
    csv_rows = count_csv_lines(csv_path)
    db_rows = conn.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
    if csv_rows == db_rows:
        logger.info("OK %s reconciled: CSV=%d DB=%d", label, csv_rows, db_rows)
    else:
        msg = f"FAIL {label} MISMATCH: CSV={csv_rows} DB={db_rows}"
        logger.error(msg)
        update_lineage(conn, run_id, ingest_status="failed", issues_log={"error": msg})
        raise RuntimeError(msg)


def main() -> None:
    run_id = generate_run_id()
    logger.info("Starting ingest | run_id=%s", run_id)

    conn = get_connection()
    init_lineage(conn, run_id)

    try:
        food_rows = load_csv_to_raw(conn, FOOD_PRICES_CSV, "food_prices", run_id)
        market_rows = load_csv_to_raw(conn, MARKETS_CSV, "markets", run_id)

        update_lineage(
            conn,
            run_id,
            raw_food_prices_rows=food_rows,
            raw_markets_rows=market_rows,
        )

        reconcile(conn, FOOD_PRICES_CSV, "food_prices", run_id, "food_prices")
        reconcile(conn, MARKETS_CSV, "markets", run_id, "markets")

        complete_lineage(conn, run_id, "completed")
        logger.info("Ingest completed successfully | run_id=%s", run_id)

    except Exception as e:
        logger.exception("Ingest failed: %s", e)
        update_lineage(conn, run_id, ingest_status="failed", issues_log={"error": str(e)})
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
