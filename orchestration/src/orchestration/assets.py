"""Dagster assets: Impect mock API -> dlt (DuckDB, impect_raw) -> dbt (main_staging / main_marts)."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import dlt
from dagster import AssetDep, AssetExecutionContext, AssetKey, AssetSpec
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, DbtProject, dbt_assets
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dagster_dlt.translator import DltResourceTranslatorData

from ingestion.source import impect_source

# --- dlt -------------------------------------------------------------------

# Repo root (orchestration/src/orchestration/assets.py -> parents[3]).
# Absolute so the warehouse is found regardless of the CWD Dagster is launched
# with — and so dlt and dbt (profiles.yml) always point at the same file.
WAREHOUSE_PATH = Path(__file__).resolve().parents[3] / "dev.duckdb"

_dlt_pipeline = dlt.pipeline(
    pipeline_name="impect",
    # Local dev warehouse file, shared by ingestion -> dbt -> dashboard.
    destination=dlt.destinations.duckdb(str(WAREHOUSE_PATH)),
    dataset_name="impect_raw",
)


class ImpectDltTranslator(DagsterDltTranslator):
    """Key each dlt resource as raw_impect_<table> (flat, 'raw' visible in the
    lineage view) so it lines up 1:1 with the dbt sources (which are remapped to
    the same keys, see ImpectDbtTranslator) — giving a continuous dlt -> dbt
    lineage graph in the Dagster UI."""

    def get_asset_spec(self, data: DltResourceTranslatorData) -> AssetSpec:
        resource = data.resource
        if resource.is_transformer:
            pipe = resource._pipe
            while pipe.has_parent:
                pipe = pipe.parent
            deps = [AssetDep(AssetKey(f"raw_impect_{pipe.name}"))]
        else:
            deps = []
        return (
            super()
            .get_asset_spec(data)
            ._replace(
                key=AssetKey(f"raw_impect_{resource.name}"),
                deps=[*deps, AssetDep(AssetKey("impect_api"))],
            )
        )


@dlt_assets(
    dlt_source=impect_source(),
    dlt_pipeline=_dlt_pipeline,
    dagster_dlt_translator=ImpectDltTranslator(),
)
def impect_dlt_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)


# --- dbt -------------------------------------------------------------------

DBT_PROJECT_DIR = Path(__file__).resolve().parents[3] / "transform"

dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROJECT_DIR)
# Ensure the manifest.json exists / is fresh so @dbt_assets can load the DAG.
dbt_project.prepare_if_dev()

_dbt = DbtCliResource(project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROJECT_DIR)


class ImpectDbtTranslator(DagsterDbtTranslator):
    """Map dbt sources (schema impect_raw, left untouched) to the flat dlt asset
    keys (raw_impect_<table>) so the lineage graph links dlt loads directly to
    the staging models that read them. Models keep their default keys."""

    def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> AssetKey:
        if dbt_resource_props.get("resource_type") == "source":
            return AssetKey(f"raw_impect_{dbt_resource_props['name']}")
        return super().get_asset_key(dbt_resource_props)


@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=ImpectDbtTranslator(),
)
def impect_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
