
--DDL Scripts

create or replace TABLE TEST.PUBLIC.CONTRACTORS (
	CONTRACTOR_NAME STRING,
	CONTRACTOR_ID STRING,
	STREET STRING,
	CITY STRING,
	STATE STRING,
	ZIP STRING,
	SUBMITTED_AT TIMESTAMP_NTZ(9) DEFAULT CURRENT_TIMESTAMP()
);

ALTER TABLE çengagements ADD COLUMN rating INTEGER;
CREATE TABLE IF NOT EXISTS TEST.PUBLIC.engagements (
    contractor_id STRING,
    customer_name STRING,
    street STRING,
    city STRING,
    state STRING,
    zip_code STRING,
    engagement_type STRING,
    activity_date DATE,
    rating INTEGER,  -- ⭐ New field
    feedback STRING,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS TEST.PUBLIC.users (
    username STRING PRIMARY KEY,
    hashed_password STRING,
    full_name STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
