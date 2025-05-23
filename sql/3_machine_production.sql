select 
    machine_name,
    date,
    weight_kg
from machine_production_waste
where order_index = 1
-- group by date
order by date desc, machine_name;
