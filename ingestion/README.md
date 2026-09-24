# Ingestion — dlt: mock API → DuckDB

Extracts the Impect data from the mock API and loads it into a DuckDB warehouse.

## How it works

- `src/ingestion/source.py` — dlt source with **5 catalog resources** (iterations,
  matches, players, squads, kpi_definitions) and **3 transformers** hanging off
  `matches` (events, player_kpis, lineups): the match list drives one API call per
  match, which makes the fan-out visible and demo-friendly.
- Nested JSON (player_kpis, lineups, events) is normalized by dlt into relational
  tables with child tables (e.g. `player_kpis__squad_home__players`).
- `write_disposition="replace"` everywhere — every run rebuilds the warehouse
  (simplest to narrate; incremental loads can be a follow-up slide).
- DuckDB file: `dev.duckdb` (local dev convention) — dbt and the dashboard read
  from this same file. Raw tables land in the `impect_raw` schema.
- Async (httpx + dlt async resources) so the ~1.6 GB of event payloads are fetched
  concurrently. Full-season run: ~4 min extract + ~7 min load.
- **Fast-iteration toggle:** `IMPECT_MAX_MATCHES=10 uv run ingestion` ingests a
  small sample of matches, evenly spread across the season (~seconds instead of
  minutes). The events transformers fan out from the match list, so one variable
  scales everything. Unset = full season. Note: with `write_disposition="replace"`
  a subset run replaces previously loaded events — rerun without the variable to
  restore the full season.

## Run

```sh
# from the project root — needs the mock API running on :8000
uv sync
uv run ingestion          # or: uv run python -m ingestion.run
```
