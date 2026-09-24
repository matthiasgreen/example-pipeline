-- Custom headline metric: Pass Success % per player per match.
-- "Of all the passes player X attempted in this match, how many reached a teammate?"
-- Computed from event data (result = 'SUCCESS' on PASS events), not from vendor
-- KPI aggregates. Passes with a missing result (e.g. end-of-half passes) are
-- excluded from the base.
{{ config(materialized='table') }}

with passes as (
    select
        match_id,
        player_id,
        squad_id,
        result
    from {{ ref('stg_impect__events') }}
    where action_type = 'PASS'
      and result is not null
),

per_player_match as (
    select
        match_id,
        player_id,
        squad_id,
        count(*)                                             as passes_attempted,
        count(*) filter (where result = 'SUCCESS')           as passes_completed,
        round(
            100.0 * count(*) filter (where result = 'SUCCESS')
            / nullif(count(*), 0),
        1)                                                   as pass_success_pct
    from passes
    group by match_id, player_id, squad_id
)

select
    p.match_id,
    p.player_id,
    p.passes_attempted,
    p.passes_completed,
    p.pass_success_pct,
    pl.common_name                    as player_name,
    s.squad_name
from per_player_match as p
left join {{ ref('stg_impect__players') }} as pl
    on p.player_id = pl.player_id
left join {{ ref('stg_impect__squads') }}  as s
    on p.squad_id = s.squad_id
