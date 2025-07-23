CREATE MATERIALIZED VIEW IF NOT EXISTS ${SCHEMA}.${CLEAN_TABLE} AS
	WITH latest_batches_per_day AS (
		SELECT DISTINCT
			DATE(batch_extraction_start) AS batch_extraction_date,
			LAST_VALUE(batch_id) OVER (
				PARTITION BY DATE(batch_extraction_start) 
				ORDER BY batch_extraction_start ASC
				ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				) AS latest_batch_id
		FROM ${SCHEMA}.${LANDING_TABLE}
	)
	
	SELECT 
		DATE(batch_extraction_start) AS date,
		property_id,
		property_type,
		price_type,
		price_pen AS price,
		additional_expense,
		address,
		region,
		city,
		district,
		NULLIF(total_size, 0) AS total_size,
		NULLIF(covered_size, 0) AS covered_size,
		NULLIF(bedrooms, 0) AS bedrooms,
		NULLIF(bathrooms, 0) AS bathrooms,
		NULLIF(half_bathrooms, 0) AS half_bathrooms,
		NULLIF(parking_spaces, 0) AS parking_spaces,
		age
	FROM ${SCHEMA}.${LANDING_TABLE} a
	INNER JOIN latest_batches_per_day b
		ON DATE(a.batch_extraction_start) = b.batch_extraction_date
		AND a.batch_id = b.latest_batch_id;