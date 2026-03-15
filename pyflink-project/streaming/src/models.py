import json
import math
from dataclasses import dataclass
from typing import Optional

@dataclass
class Ride:
    lpep_pickup_datetime: str
    lpep_dropoff_datetime: str
    PULocationID: int
    DOLocationID: int
    passenger_count: Optional[int]
    trip_distance: float
    tip_amount: float
    total_amount: float

def safe_optional_int(value):
    if value is None:
        return None
    if math.isnan(value):
        return None
    return int(value)

def ride_from_row(row):
    return Ride(
        lpep_pickup_datetime=str(row.lpep_pickup_datetime),
        lpep_dropoff_datetime=str(row.lpep_dropoff_datetime),
        PULocationID=int(row.PULocationID),
        DOLocationID=int(row.DOLocationID),
        passenger_count=safe_optional_int(row.passenger_count),
        trip_distance=float(row.trip_distance),
        tip_amount=float(row.tip_amount),
        total_amount=float(row.total_amount),
    )


def ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return Ride(**ride_dict)