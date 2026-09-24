# orchestration — Dagster

Orchestrates the pipeline as assets:

```
impect_api (mock API, external asset)
  └─ raw_impect_{iterations,matches,players,squads,events}   (dlt, dagster-dlt)
       └─ staging/stg_impect__*                              (dbt, dagster-dbt)
            └─ marts/player_match_metrics                    (dbt)
                 └─ streamlit_dashboard (external, reads DuckDB directly)
```

- dlt source reused from the `ingestion` package (`ingestion.source.impect_source`).
- dlt assets are keyed `raw_impect_<table>` (flat, so "raw" is visible in the
  lineage view) via `ImpectDltTranslator`, and the dbt sources (schema
  `impect_raw`, left untouched) are remapped to the same keys via
  `ImpectDbtTranslator` — so the lineage graph in the Dagster UI is continuous
  dlt → dbt.
- dbt tests are surfaced as Dagster asset checks.

## Run

```bash
# from the project root, with the mock API running in another terminal:
cd api && uv run uvicorn api.main:app --port 8000
# launch the Dagster UI (works from the repo root or orchestration/):
uv run dg dev
# or the plain dagster CLI:
DAGSTER_HOME=.dagster uv run dagster dev -m orchestration.definitions
```

The repo root `pyproject.toml` declares a `dg` workspace containing the
`orchestration` project; `orchestration/.env` points dg at the shared uv
workspace venv (`DG_PROJECT_PYTHON_EXECUTABLE=../.venv/bin/python`).
Set `DAGSTER_HOME` to persist runs across webserver restarts. The
fast-iteration toggle from ingestion still works: `IMPECT_MAX_MATCHES=10`
before launching.

## Notes

- The warehouse path is resolved absolutely (`<repo>/dev.duckdb`), so Dagster can
  be launched from any directory — same file as `uv run ingestion` and the dbt
  profile.
- The mock API must be up before materializing the dlt assets.
