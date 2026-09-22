# pyright: basic

import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException

DATA_DIR = Path(__file__).resolve().parents[3] / "source_data" / "data"
ITERATION_ID = 743  # Bundesliga 2023/24


app = FastAPI(
    title="Mock Impect Open Data API",
    description=("Mock vendor API serving Impect Bundesliga 2023/24 open data."),
)


@lru_cache(maxsize=64)
def load(rel_path: str):
    file = DATA_DIR / rel_path
    if not file.exists():
        raise HTTPException(404, detail=f"Unknown resource: {rel_path}")
    return json.loads(file.read_text())


@app.get("/iterations", tags=["catalog"])
def iterations():
    """Available competition seasons."""
    return load("iterations.json")


@app.get("/iterations/{iteration_id}/matches", tags=["catalog"])
def matches(iteration_id: int):
    """All matches of a season."""
    data = load("matches/matches_743.json")
    if iteration_id != ITERATION_ID:
        raise HTTPException(404, detail=f"No matches for iteration {iteration_id}")
    return data


@app.get("/players", tags=["catalog"])
def players():
    """Player master data."""
    return load("players/players_743.json")


@app.get("/squads", tags=["catalog"])
def squads():
    """Squad (club) master data."""
    return load("squads/squads_743.json")


@app.get("/kpi-definitions", tags=["catalog"])
def kpi_definitions():
    """KPI catalog: id, name, label, definition."""
    return load("kpi_definitions.json")


@app.get("/matches/{match_id}/events", tags=["match data"])
def events(match_id: int):
    """Raw event data for one match."""
    return load(f"events/events_{match_id}.json")


@app.get("/matches/{match_id}/events-kpis", tags=["match data"])
def events_kpis(match_id: int):
    """KPI values on event level for one match."""
    return load(f"events_kpis/events_kpis_{match_id}.json")


@app.get("/matches/{match_id}/player-kpis", tags=["match data"])
def player_kpis(match_id: int):
    """KPI aggregates per player per position per match."""
    return load(f"player_kpis/player_kpis_{match_id}.json")


@app.get("/matches/{match_id}/lineup", tags=["match data"])
def lineup(match_id: int):
    """Lineups and substitutions for one match."""
    return load(f"lineups/lineups_{match_id}.json")
