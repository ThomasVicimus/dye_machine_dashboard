select 
    machine_name,
    state,
    user_prompt,
    num_of_alarms,
    mt_temperature,
    batch_no,
    current_step,
    next_step,
    minutes_run,
    expected_finish_time
from machine_status
order by machine_name;