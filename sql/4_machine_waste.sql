select 
    machine_name,
    water_ton,
    power_kwh,
    steam_ton,
    order_index,
    period
from machine_production_waste
    where period = '{period_replace}'
