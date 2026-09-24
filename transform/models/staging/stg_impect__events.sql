-- Lean, typed view over the raw event stream.
-- One row = one on-ball event in one match.
with source as (
    select * from {{ source('impect_raw', 'events') }}
),

renamed as (
    select
        -- identifiers
        id                                         as event_id,
        match_id                                   as match_id,
        squad_id                                   as squad_id,
        player__id                                 as player_id,
        player__position                           as player_position,
        player__position_side                      as player_position_side,
        current_attacking_squad_id                 as current_attacking_squad_id,
        pressing_player_id                         as pressing_player_id,
        fouled_player_id                           as fouled_player_id,
        duel__player_id                            as duel_player_id,

        -- event taxonomy
        action_type                                as action_type,
        action                                     as action,
        phase                                      as phase,
        result                                     as result,
        period_id                                  as period_id,
        sequence_index                             as sequence_index,
        duration                                   as duration,
        pressure                                   as pressure,
        opponents                                  as opponents,
        distance_to_goal                           as distance_to_goal,
        distance_to_opponent                       as distance_to_opponent,
        body_part                                  as body_part,

        -- timing
        game_time__game_time                       as game_time,
        game_time__game_time_in_sec                as game_time_in_sec,

        -- ball locations (own goal x=-52.5, opponent goal x=+52.5)
        start__coordinates__x                      as start_x,
        start__coordinates__y                      as start_y,
        end__coordinates__x                        as end_x,
        end__coordinates__y                        as end_y,
        start__pitch_position                      as start_pitch_position,
        end__pitch_position                        as end_pitch_position,
        start__lane                                as start_lane,
        end__lane                                  as end_lane,
        start__packing_zone                        as start_packing_zone,
        end__packing_zone                          as end_packing_zone,

        -- pass attributes
        pass__distance                             as pass_distance,
        pass__angle                                as pass_angle,
        pass__receiver__player_id                  as pass_receiver_player_id,
        pass__receiver__type                       as pass_receiver_type,

        -- duel / shot attributes
        duel__duel_type                            as duel_type,
        shot__distance                             as shot_distance,
        shot__angle                                as shot_angle,

        -- expected possession value (pxT)
        px_t__team                                 as px_t_team,
        px_t__opponent                             as px_t_opponent
    from source
)

select * from renamed
