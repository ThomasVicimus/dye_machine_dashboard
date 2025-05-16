select 
    ms.machine_name,
    ms.state,
    ms.user_prompt,
    ms.num_of_alarms,
    ms.mt_temperature,
    ms.batch_no,
    ms.current_step,
    ms.next_step,
    ms.minutes_run,
    ms.expected_finish_time,
    bq.total_steps_cnt,
    bq.current_step_cnt
from machine_status ms LEFT JOIN 
    (SELECT 
        machine_name,
        max(position) as total_steps_cnt,
        min(position) as current_step_cnt
    FROM batch_queued
    GROUP BY machine_name
    ) bq
    ON ms.machine_name = bq.machine_name