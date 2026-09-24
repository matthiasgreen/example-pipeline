"""Dagster definitions entry point (`dagster dev -m orchestration.definitions`)."""

from dagster import AssetKey, AssetSpec, Definitions, SourceAsset
from dagster_dlt import DagsterDltResource
from orchestration.assets import _dbt, impect_dbt_assets, impect_dlt_assets

# External "source system" node: the FastAPI mock API serving the Impect open data.
impect_api = SourceAsset(key=AssetKey("impect_api"), group_name="impect_source")

# External consumption node: the Streamlit dashboard (dashboard/app.py) reads the
# warehouse directly — the player metrics mart plus match metadata for the x-axis.
# skippable=True: it's an app, not something Dagster materializes.
streamlit_dashboard = AssetSpec(
    key=AssetKey("streamlit_dashboard"),
    skippable=True,
    group_name="dashboard",
    description=(
        "Streamlit app (dashboard/app.py): pick a player, see their Pass Success % "
        "per match across the season. Reads DuckDB directly via "
        "main_marts.player_match_metrics (joined with main_staging.stg_impect__matches "
        "for match day / date). Run: uv run streamlit run dashboard/app.py"
    ),
    deps=[
        AssetKey(["marts", "player_match_metrics"]),
        AssetKey(["staging", "stg_impect__matches"]),
    ],
)

defs = Definitions(
    assets=[impect_dlt_assets, impect_dbt_assets, impect_api, streamlit_dashboard],
    resources={
        "dlt": DagsterDltResource(),
        "dbt": _dbt,
    },
)
