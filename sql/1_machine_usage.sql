select 
    machine_name,
    run,
    idle,
    down,
    repair,
    order_index,
    period
from overall_usage
    where period = '{period_replace}'
