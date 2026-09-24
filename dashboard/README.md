# Dashboard — Streamlit app

Single-file Streamlit app reading directly from the DuckDB warehouse
(`dev.duckdb`, mart `main_marts.player_match_metrics`).

Run from the repo root:

```bash
uv run streamlit run dashboard/app.py
```

Pick a player from the dropdown → see their pass success rate (%) across
the matches of the Bundesliga 2023/24 season.
