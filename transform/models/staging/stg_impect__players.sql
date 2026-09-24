with source as (
    select * from {{ source('impect_raw', 'players') }}
),

renamed as (
    select
        id                  as player_id,
        firstname,
        lastname,
        commonname          as common_name,
        birthdate           as birthdate,
        birthplace          as birthplace,
        leg,
        gender,
        current_squad_id    as current_squad_id
    from source
)

select * from renamed
