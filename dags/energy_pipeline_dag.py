"""
Main DAG for the DSS150P Group Eta data engineering pipeline.

Structure:
    extract_all -> validate_raw -> transform_staging -> transform_curated
                                                              |
                                                              v
                                                    validate_curated
                                                              |
                                                              v
                                                      load_postgres

The task bodies currently call the ingestion orchestrator (already implemented).
Later phases will replace the placeholder transformations with modular
transformation modules (src.transform.*).
"""
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

# ---------------------------------------------------------------------------
# DAG default arguments
# ---------------------------------------------------------------------------
default_args = {
    "owner": "gab",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
}

PROJECT_DIR = Path("/opt/airflow/project")

with DAG(
    dag_id="energy_pipeline",
    description="End-to-end pipeline: ingestion -> validation -> transformation -> curated -> Postgres",
    default_args=default_args,
    start_date=datetime(2026, 10, 1),
    schedule="0 2 * * *",   # daily at 02:00 UTC
    catchup=False,
    max_active_runs=1,      # prevent overlapping runs
    tags=["dss150p", "group-eta", "energy"],
) as dag:

    # ────────────────────────────────────────────────────────────
    # Start marker
    # ────────────────────────────────────────────────────────────
    start = EmptyOperator(task_id="start")

    # ────────────────────────────────────────────────────────────
    # STAGE 1 — Extraction (Gab)
    # ────────────────────────────────────────────────────────────
    extract_all = BashOperator(
        task_id="extract_all",
        bash_command=f"cd {PROJECT_DIR} && python -m src.extract.run_ingestion",
        append_env=True,
    )

    # ────────────────────────────────────────────────────────────
    # STAGE 2 — Raw validation (Iya)
    # Placeholder — Iya's validation modules will replace this.
    # ────────────────────────────────────────────────────────────
    validate_raw = BashOperator(
        task_id="validate_raw",
        bash_command='echo "[PLACEHOLDER] Raw validation will run here once Iya\'s validation modules are ready."',
    )

    # ────────────────────────────────────────────────────────────
    # STAGE 3 — Staging transformation (Sophia)
    # Placeholder — Sophia's src.transform.clean_* modules will replace this.
    # ────────────────────────────────────────────────────────────
    transform_staging = BashOperator(
        task_id="transform_staging",
        bash_command='echo "[PLACEHOLDER] Staging transformation will run here once Sophia\'s transform modules are ready."',
    )

    # ────────────────────────────────────────────────────────────
    # STAGE 4 — Curated transformation (Sophia)
    # ────────────────────────────────────────────────────────────
    transform_curated = BashOperator(
        task_id="transform_curated",
        bash_command='echo "[PLACEHOLDER] Curated integration will run here once Sophia\'s three-source merge is modularized."',
    )

    # ────────────────────────────────────────────────────────────
    # STAGE 5 — Curated validation (Iya)
    # ────────────────────────────────────────────────────────────
    validate_curated = BashOperator(
        task_id="validate_curated",
        bash_command='echo "[PLACEHOLDER] Curated validation will run here once Iya\'s data-quality checks are ready."',
    )

    # ────────────────────────────────────────────────────────────
    # STAGE 6 — PostgreSQL load (Sophia)
    # ────────────────────────────────────────────────────────────
    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command='echo "[PLACEHOLDER] Curated data will be loaded into Postgres once Sophia\'s schema is finalized."',
    )

    # ────────────────────────────────────────────────────────────
    # End marker
    # ────────────────────────────────────────────────────────────
    end = EmptyOperator(task_id="end")

    # ────────────────────────────────────────────────────────────
    # Task dependencies
    # ────────────────────────────────────────────────────────────
    start >> extract_all
    extract_all >> validate_raw
    validate_raw >> transform_staging
    transform_staging >> transform_curated
    transform_curated >> validate_curated
    validate_curated >> load_postgres
    load_postgres >> end