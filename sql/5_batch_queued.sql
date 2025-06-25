SELECT
    machine_name,
    state,
    batch_no,
    color,
    -- color_text,
    -- color_code,
    -- position,
    start_time,
    expected_run_minutes
from batch_queued
where start_time >= '{min_start_time}' and start_time < '{max_start_time}'
order by machine_name;