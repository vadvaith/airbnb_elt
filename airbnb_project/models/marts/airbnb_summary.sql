{{ config(materialized='table') }}

select
    room_type,
    count(*) as total_listings,
    avg(price) as avg_price,
    avg(availability_365) as avg_availability
from {{ ref('stg_airbnb_listings') }}
group by room_type