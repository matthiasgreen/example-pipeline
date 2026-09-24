import duckdb
import plotly.express as px
import streamlit as st

DB_PATH = "dev.duckdb"

st.set_page_config(page_title="Pass Success %", page_icon="⚽", layout="wide")
st.title("⚽ Pass Success Rate — Bundesliga 2023/24")


@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)


con = get_connection()

players = con.sql(
    """
    select
        player_id,
        any_value(player_name)   as player_name,
        any_value(squad_name)    as squad_name,
        count(*)                 as matches
    from main_marts.player_match_metrics
    where player_name is not null
    group by player_id
    order by player_name
    """
).df()

players["label"] = players["player_name"] + " (" + players["squad_name"] + ")"

player_label = st.selectbox(
    "Select a player",
    options=players["label"],
    index=players["label"].tolist().index("Jamal Musiala (FC Bayern München)")
    if "Jamal Musiala (FC Bayern München)" in players["label"].tolist()
    else 0,
)

row = players.loc[players["label"] == player_label].iloc[0]

data = con.sql(
    """
    select
        m.match_day,
        any_value(m.match_day_name)  as match_day_name,
        min(m.scheduled_date)        as scheduled_date,
        p.player_name,
        p.squad_name,
        p.pass_success_pct,
        p.passes_attempted,
        p.passes_completed
    from main_marts.player_match_metrics as p
    join main_staging.stg_impect__matches as m
        on p.match_id = m.match_id
    where p.player_id = ?
    group by m.match_day, p.player_name, p.squad_name,
             p.pass_success_pct, p.passes_attempted, p.passes_completed
    order by m.match_day
    """,
    params=[int(row["player_id"])],
).df()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Matches", len(data))
c2.metric("Avg pass success %", f"{data['pass_success_pct'].mean():.1f}")
c3.metric("Best match", f"{data['pass_success_pct'].max():.1f}")
c4.metric("Total passes", int(data["passes_attempted"].sum()))  # pyright: ignore[reportArgumentType]

fig = px.line(
    data,
    x="scheduled_date",
    y="pass_success_pct",
    markers=True,
    labels={
        "scheduled_date": "Match date",
        "pass_success_pct": "Pass success %",
    },
    title=f"{row['player_name']} — pass success rate across the season",
    hover_data={
        "match_day_name": True,
        "passes_attempted": True,
        "passes_completed": True,
        "scheduled_date": False,
        "pass_success_pct": ":.1f",
    },
)
fig.update_traces(line_color="#005F53", marker_color="#005F53")
fig.update_layout(yaxis_range=[0, 100])

st.plotly_chart(fig, use_container_width=True)
st.caption("Data: Impect open data, Bundesliga 2023/24 — via dlt → DuckDB → dbt.")
