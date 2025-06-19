select 
    machine_name,
    water_ton/weight_kg as water_ton,
    power_kwh/weight_kg as power_kwh,
    steam_ton/weight_kg as steam_ton,
    order_index,
    period
    -- *
from machine_production_waste
    where period = '{period_replace}'
