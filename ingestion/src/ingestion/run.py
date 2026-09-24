"""Run the ingestion: mock API -> dlt -> DuckDB.

Usage (from project root): uv run ingestion
"""
import dlt

from ingestion.source import impect_source


def run():
    pipeline = dlt.pipeline(
        pipeline_name="impect",
        # Local dev warehouse file, shared by ingestion -> dbt -> dashboard.
        # Provider identity lives in the schema (impect_raw), not the database.
        destination=dlt.destinations.duckdb("dev.duckdb"),
        dataset_name="impect_raw",
    )
    info = pipeline.run(impect_source())
    print(info)


if __name__ == "__main__":
    run()
