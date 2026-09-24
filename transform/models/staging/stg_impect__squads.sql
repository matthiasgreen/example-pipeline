with source as (
    select * from {{ source('impect_raw', 'squads') }}
),

renamed as (
    select
        id          as squad_id,
        name        as squad_name,
        country_id  as country_id,
        type,
        gender,
        image_url   as image_url
    from source
)

select * from renamed
