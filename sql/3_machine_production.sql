select 
    date,
    sum(weight_kg) as weight_kg
from machine_production_waste
where order_index = 1
group by date
order by date desc;
