from jinja2 import Template
# Data is only going to be from regions LIMA and CALLAO

GET_REGIONS_TEMPLATE = Template("""
SELECT DISTINCT region
FROM {{ schema }}.{{ table }}
WHERE region IN ('LIMA', 'CALLAO')
ORDER BY region
""")

GET_CITIES_TEMPLATE = Template("""
SELECT DISTINCT city
FROM {{ schema }}.{{ table }}
WHERE region = %s AND region IN ('LIMA', 'CALLAO')
ORDER BY city
""")

GET_DISTRICTS_TEMPLATE = Template("""
SELECT DISTINCT district
FROM {{ schema }}.{{ table }}
WHERE region = %s AND region IN ('LIMA', 'CALLAO')
AND city = %s
ORDER BY district
""")

GET_PRICE_TYPES_TEMPLATE = Template("""
SELECT DISTINCT price_type
FROM {{ schema }}.{{ table }}
ORDER BY price_type
""")

GET_FILTERED_PROPERTIES_TEMPLATE = Template("""
SELECT
    region,
    city,
    district,
    price / COALESCE(NULLIF(total_size, 0), covered_size) AS price_per_size,
    price,
    total_size,
    covered_size,
    price_type,
    date
FROM {{ schema }}.{{ table }}
WHERE price / COALESCE(NULLIF(total_size, 0), covered_size) < 100
AND price / COALESCE(NULLIF(total_size, 0), covered_size) > 10
AND COALESCE(NULLIF(total_size, 0), covered_size) >= 10
AND COALESCE(NULLIF(total_size, 0), covered_size) <= 200
AND {{ filters }}
""")
