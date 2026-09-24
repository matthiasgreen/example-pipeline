# pyright: basic
import os

import dlt
import httpx

BASE_URL = os.environ.get("IMPECT_API_URL", "http://localhost:8000")
ITERATION_ID = 743  # Bundesliga 2023/24

# --- Fast-iteration toggle ---------------------------------------------------
# Set IMPECT_MAX_MATCHES (e.g. 10) to only ingest a small sample of matches,
# spread evenly across the season — cuts the ~5 min full-season run down to
# seconds. Unset = full season (306 matches).
# NOTE: everything is loaded with write_disposition="replace", so a subset run
# REPLACES previously loaded events. Rerun without the variable to restore the
# full season before any "season stats" demo.
_raw_max_matches = os.environ.get("IMPECT_MAX_MATCHES", "").strip()
MAX_MATCHES = int(_raw_max_matches) if _raw_max_matches.isdigit() else None

_client = httpx.AsyncClient(base_url=BASE_URL, timeout=300)


def strip(item: dict, *keys: str) -> dict:
    """Remove fields we don't need (avoids noisy child tables for key-mapping lists)."""
    for k in keys:
        item.pop(k, None)
    return item


async def get(path: str):
    r = await _client.get(path)
    r.raise_for_status()
    return r.json()


@dlt.resource(name="iterations", write_disposition="replace")
async def iterations():
    for it in await get("/iterations"):
        yield strip(it, "idMappings")


@dlt.resource(name="matches", write_disposition="replace", primary_key="id")
async def matches():
    all_matches = await get(f"/iterations/{ITERATION_ID}/matches")
    if MAX_MATCHES is not None and len(all_matches) > MAX_MATCHES:
        # Evenly spaced sample so all clubs and phases of the season are represented.
        step = len(all_matches) // MAX_MATCHES
        all_matches = all_matches[::step][:MAX_MATCHES]
        print(
            f"[impect] IMPECT_MAX_MATCHES={MAX_MATCHES}: "
            f"ingesting {len(all_matches)} of 306 matches"
        )
    for m in all_matches:
        yield strip(m, "idMappings")


@dlt.transformer(name="events", data_from=matches, write_disposition="replace", primary_key="id")
async def events(match):
    """Raw event data, one call per match."""
    # The vendor's events payload is a bare list without a match reference,
    # so we stamp the parent match id onto every event.
    for event in await get(f"/matches/{match['id']}/events"):
        yield {**event, "matchId": match["id"]}


@dlt.resource(
    name="players",
    write_disposition="replace",
    primary_key="id",
)
async def players():
    for p in await get("/players"):
        yield strip(p, "idMappings", "countryIds")


@dlt.resource(name="squads", write_disposition="replace", primary_key="id")
async def squads():
    for s in await get("/squads"):
        yield strip(s, "idMappings")


@dlt.source(name="impect")
def impect_source():
    return [iterations, matches, players, squads, events]
