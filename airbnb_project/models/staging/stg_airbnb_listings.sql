{{ config(materialized='view') }}

select
    cast(id as string) as id,
    name,
    cast(host_id as string) as host_id,
    host_name,
    neighbourhood,
    try_to_double(latitude) as latitude,
    try_to_double(longitude) as longitude,
    room_type,
    try_to_number(regexp_replace(price, '[^0-9.]', '')) as price,
    try_to_number(minimum_nights) as minimum_nights,
    try_to_number(number_of_reviews) as number_of_reviews,
    last_review,
    try_to_double(reviews_per_month) as reviews_per_month,
    try_to_number(calculated_host_listings_count) as calculated_host_listings_count,
    try_to_number(availability_365) as availability_365,
    try_to_number(number_of_reviews_ltm) as number_of_reviews_ltm
from {{ source('raw', 'AIRBNB_LISTINGS') }}
where try_to_double(latitude) is not null
  and try_to_double(longitude) is not null