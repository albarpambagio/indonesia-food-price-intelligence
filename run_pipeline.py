import logging
import shutil
import subprocess
import sys
import time
from pathlib import Path

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
TRANSFORM_LOG_FILE = "logs/transform.log"
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

transform_log_handler = logging.FileHandler(TRANSFORM_LOG_FILE)
transform_log_handler.setFormatter(logging.Formatter(LOG_FORMAT))


def step(name: str) -> None:
    logger.info("=== STEP: %s ===", name)


def run_python(script_path: str, cwd: str, step_label: str) -> None:
    logger.info("Running %s ...", step_label)
    result = subprocess.run(
        ["uv", "run", "python", script_path],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("%s FAILED\n%s", step_label, result.stderr.strip() or result.stdout.strip())
        raise RuntimeError(f"{step_label} failed")
    logger.info("%s OK", step_label)
    for line in result.stdout.splitlines():
        line = line.strip()
        if line and not line.startswith("="):
            logger.info("  %s", line)


def run_dbt(command: list[str]) -> None:
    logger.info("Running dbt %s ...", " ".join(command))
    logger.addHandler(transform_log_handler)
    result = subprocess.run(
        ["uv", "run", "dbt"] + command,
        cwd="transform",
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("dbt %s FAILED\n%s", " ".join(command), result.stderr.strip() or result.stdout.strip())
        logger.removeHandler(transform_log_handler)
        raise RuntimeError(f"dbt {' '.join(command)} failed")
    logger.info("dbt %s OK", " ".join(command))
    for line in result.stdout.splitlines():
        if "PASS" in line or "WARN" in line or "ERROR" in line or "Completed" in line:
            logger.info("  %s", line.strip())
    logger.removeHandler(transform_log_handler)


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


def reconcile_mart(
    conn: duckdb.DuckDBPyConnection,
    label: str,
    target_table: str,
) -> int:
    target_count = conn.execute(f"SELECT COUNT(*) FROM {target_table}").fetchone()[0]
    if target_count > 0:
        logger.info("  OK %s: %d rows", label, target_count)
    else:
        msg = f"  FAIL {label}: 0 rows"
        logger.error(msg)
        raise RuntimeError(msg)
    return target_count


def copy_dbt_artifacts(run_id: str) -> None:
    artifacts_path = Path("transform/target/run_results.json")
    if artifacts_path.exists():
        dest = Path(f"logs/dbt_run_results_{run_id}.json")
        shutil.copy(str(artifacts_path), str(dest))
        logger.info("  dbt artifacts copied to %s", dest)


def get_connection_safe() -> duckdb.DuckDBPyConnection | None:
    for attempt in range(2):
        try:
            return get_connection()
        except Exception:
            if attempt == 0:
                time.sleep(1)
    return None


current_step_map: dict[str, str] = {}

def main() -> None:
    start = time.time()
    run_id = generate_run_id()
    logger.info("Pipeline start | run_id=%s", run_id)

    conn = get_connection()
    init_lineage(conn, run_id)
    conn.close()

    current_step = "pipeline_status"
    current_step_name = "pipeline"
    current_step_map.clear()

    try:
        # --- Step 1: Ingest ---
        current_step = "ingest_status"
        current_step_name = "ingest"
        step("Ingest")
        result = subprocess.run(
            ["uv", "run", "python", "load_raw.py"],
            cwd="ingest",
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error("Ingest failed\n%s", result.stderr)
            raise RuntimeError("Ingest failed")
        for line in result.stdout.splitlines():
            if line.strip():
                logger.info("  %s", line.strip())

        conn = get_connection()
        raw_food = conn.execute("SELECT COUNT(*) FROM raw.food_prices").fetchone()[0]
        raw_markets = conn.execute("SELECT COUNT(*) FROM raw.markets").fetchone()[0]
        update_lineage(conn, run_id, raw_food_prices_rows=raw_food, raw_markets_rows=raw_markets)
        conn.close()

        # --- Step 2: dbt seed (islamic calendar) ---
        current_step = "transform_status"
        current_step_name = "dbt seed"
        step("dbt seed")
        run_dbt(["seed"])

        # --- Step 3: dbt run (staging + intermediate + marts) ---
        current_step = "transform_status"
        current_step_name = "dbt run"
        step("dbt run")
        conn = get_connection()
        update_lineage(conn, run_id, transform_status="running")
        conn.close()
        run_dbt(["run"])
        copy_dbt_artifacts(run_id)

        # --- Step 4: dbt test ---
        current_step = "transform_status"
        current_step_name = "dbt test"
        step("dbt test")
        run_dbt(["test"])

        # --- Step 5: Row count reconciliation ---
        step("Row count reconciliation")
        conn = get_connection()
        stg_food = reconcile_layer(
            conn, "food_prices: raw -> staging", raw_food, "wfp_staging.stg_food_prices"
        )
        reconcile_layer(
            conn, "markets: raw -> staging", raw_markets, "wfp_staging.stg_markets"
        )
        reconcile_layer(
            conn, "food_prices: staging -> int_prices_normalised",
            stg_food, "wfp_intermediate.int_prices_normalised",
        )

        # Mart reconciliation (verify each mart has rows)
        step("Mart reconciliation")
        mart_trends = reconcile_mart(conn, "mart_price_trends", "wfp_marts.mart_price_trends")
        mart_seasonal = reconcile_mart(conn, "mart_seasonal_patterns", "wfp_marts.mart_seasonal_patterns")
        mart_geo = reconcile_mart(conn, "mart_geo_disparity", "wfp_marts.mart_geo_disparity")
        mart_corr = reconcile_mart(conn, "mart_commodity_correlation", "wfp_marts.mart_commodity_correlation")
        mart_corr_summary = reconcile_mart(conn, "mart_correlation_summary", "wfp_marts.mart_correlation_summary")

        update_lineage(
            conn, run_id,
            transform_status="completed",
            issues_log={
                "mart_price_trends_rows": mart_trends,
                "mart_seasonal_patterns_rows": mart_seasonal,
                "mart_geo_disparity_rows": mart_geo,
                "mart_commodity_correlation_rows": mart_corr,
                "mart_correlation_summary_rows": mart_corr_summary,
            },
        )
        conn.close()

        # --- Step 6: Forecast ---
        current_step = "forecast_status"
        current_step_name = "forecast"
        step("Forecast")
        conn = get_connection()
        update_lineage(conn, run_id, forecast_status="running")
        conn.close()
        run_python("forecast/run_forecast.py", ".", "Forecast")

        # --- Step 7: Export to JSON ---
        current_step = "export_status"
        current_step_name = "export"
        step("Export to JSON")
        conn = get_connection()
        update_lineage(conn, run_id, export_status="running")
        conn.close()
        run_python("export/export_json.py", ".", "Export")

        # --- Step 8: Complete ---
        conn = get_connection()
        complete_lineage(conn, run_id, "completed")
        conn.close()

        elapsed = time.time() - start
        logger.info("Pipeline completed | run_id=%s | elapsed=%.1fs", run_id, elapsed)

    except Exception as e:
        logger.exception("Pipeline failed at step '%s': %s", current_step_name, e)
        fail_conn = get_connection_safe()
        if fail_conn:
            try:
                update_lineage(fail_conn, run_id, **{current_step: "failed"}, issues_log={"error": str(e), "step": current_step_name})
                fail_conn.close()
            except Exception:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
