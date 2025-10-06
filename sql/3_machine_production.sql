select 
    machine_name,
    date,
    weight_kg,
    order_index
from production_volume_log
where period in ({period_replace})
-- where order_index = 1
-- group by date
order by date, machine_name;
