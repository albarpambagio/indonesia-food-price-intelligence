import logging
import subprocess
import sys
import time

import duckdb

from ingest.config import (
    DB_PATH,
    generate_run_id,
    get_connection,
    init_lineage,
    update_lineage,
    complete_lineage,
)

LOG_FILE = "logs/pipeline_run.log"
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


def step(name: str) -> None:
    logger.info("=== STEP: %s ===", name)


def run_dbt(command: list[str]) -> None:
    logger.info("Running dbt %s ...", " ".join(command))
    result = subprocess.run(
        ["uv", "run", "dbt"] + command,
        cwd="transform",
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("dbt %s FAILED\n%s", " ".join(command), result.stderr.strip() or result.stdout.strip())
        raise RuntimeError(f"dbt {' '.join(command)} failed")
    logger.info("dbt %s OK", " ".join(command))
    for line in result.stdout.splitlines():
        if "PASS" in line or "WARN" in line or "ERROR" in line or "Completed" in line:
            logger.info("  %s", line.strip())


def reconcile_layer(
    conn: duckdb.DuckDBPyConnection,
    label: str,
    source_count: int,
    target_table: str,
) -> int:
    target_count = conn.execute(f"SELECT COUNT(*) FROM {target_table}").fetchone()[0]
    if source_count == target_count:
        logger.info("  OK %s: source=%d target=%d", label, source_count, target_count)
    else:
        msg = f"  FAIL {label} MISMATCH: source={source_count} target={target_count}"
        logger.error(msg)
        raise RuntimeError(msg)
    return target_count


def main() -> None:
    start = time.time()
    run_id = generate_run_id()
    logger.info("Pipeline start | run_id=%s", run_id)

    conn = get_connection()
    init_lineage(conn, run_id)

    try:
        # --- Step 1: Ingest ---
        step("Ingest")
        conn.close()
        result = subprocess.run(
            ["uv", "run", "python", "load_raw.py"],
            cwd="ingest",
            capture_output=True,
            text=True,
        )
        conn = get_connection()
        if result.returncode != 0:
            logger.error("Ingest failed\n%s", result.stderr)
            raise RuntimeError("Ingest failed")
        for line in result.stdout.splitlines():
            if line.strip():
                logger.info("  %s", line.strip())
        raw_food = conn.execute("SELECT COUNT(*) FROM raw.food_prices").fetchone()[0]
        raw_markets = conn.execute("SELECT COUNT(*) FROM raw.markets").fetchone()[0]
        update_lineage(conn, run_id, raw_food_prices_rows=raw_food, raw_markets_rows=raw_markets)
        conn.close()

        # --- Step 2: dbt run (staging) ---
        step("dbt run (staging)")
        run_dbt(["run", "--select", "staging"])

        # --- Step 3: dbt test ---
        step("dbt test")
        run_dbt(["test"])

        # --- Step 4: Row count reconciliation ---
        step("Row count reconciliation")
        conn = get_connection()
        update_lineage(conn, run_id, transform_status="running")
        stg_food = reconcile_layer(conn, "food_prices: raw -> staging", raw_food, "wfp_staging.stg_food_prices")
        reconcile_layer(conn, "markets: raw -> staging", raw_markets, "wfp_staging.stg_markets")

        # --- Step 5: Complete ---
        update_lineage(conn, run_id, transform_status="completed")
        complete_lineage(conn, run_id, "completed")

        elapsed = time.time() - start
        logger.info("Pipeline completed | run_id=%s | elapsed=%.1fs", run_id, elapsed)

    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        try:
            update_lineage(conn, run_id, ingest_status="failed", issues_log={"error": str(e)})
        except Exception:
            pass
        sys.exit(1)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Write pipeline summary
    logger.info("=== Pipeline Summary ===")
    logger.info("run_id: %s", run_id)
    logger.info("status: completed")
    logger.info("elapsed: %.1fs", time.time() - start)


if __name__ == "__main__":
    main()
