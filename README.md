# Football Analytics Data Pipeline

A demo ELT pipeline for football event data, built for a masterclass presentation.

It takes the openly available [Impect](https://www.impect.com) Bundesliga 2023/24
dataset and runs it through a modern data stack — mock API → dlt → DuckDB → dbt —
orchestrated with Dagster, and serves it in a dashboard where you pick a player and
see how they compare to the rest of the league on a metric (e.g. pass success %).

The Python code is organized as a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/):
one shared virtual environment, one `pyproject.toml` per component.

## Data

[ImpectAPI/open-data](https://github.com/ImpectAPI/open-data) — event data, event
and player KPIs, lineups, and metadata for all 306 matches of the Bundesliga
2023/24 season. Credit: Impect is the data provider (see their license terms).
