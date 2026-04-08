# Batch 2.3 Canonical Silver Schema

## Purpose
Define canonical relational silver structures after flattening nested raw events.

## Silver Tables

### 1. `silver_events`
Core event-level fact table with harmonized dimensions and session reference.

Columns:
- event_id
- source_name
- source_file_id
- event_name
- event_timestamp
- event_date
- user_pseudo_id
- source_channel
- campaign_name
- device_type
- device_os
- country_code
- country_name
- city_name
- session_seq
- session_start_ts
- session_id

### 2. `silver_event_params`
Unnested key-value bridge from raw `event_params`.

Columns:
- event_id
- param_key
- param_value

### 3. `silver_event_items`
Unnested item-level bridge from raw `items` arrays.

Columns:
- event_id
- item_index
- item_id
- item_name
- item_category
- quantity
- price

### 4. `silver_sessions`
Sessionized table with 30-minute inactivity rule.

Columns:
- session_id
- user_pseudo_id
- session_start_ts
- session_end_ts
- event_count

### 5. Canonical dimensions
- `dim_channel`: channel_id, source_channel
- `dim_campaign`: campaign_id, campaign_name, source_channel
- `dim_device`: device_id, device_type, device_os
- `dim_geography`: geo_id, country_code, country_name, city_name

## Deterministic Session Rule
- Sort events by `user_pseudo_id`, `event_timestamp`.
- Start a new session when gap between consecutive user events is greater than 30 minutes.
- Build `session_id` as deterministic tuple of user and session start timestamp.
