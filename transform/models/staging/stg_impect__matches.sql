with source as (
    select * from {{ source('impect_raw', 'matches') }}
),

renamed as (
    select
        iteration_id                as iteration_id,
        id                          as match_id,
        home_squad_id               as home_squad_id,
        away_squad_id               as away_squad_id,
        scheduled_date              as scheduled_date,
        match_day__index            as match_day,
        match_day__name             as match_day_name
    from source
)

select * from renamed
