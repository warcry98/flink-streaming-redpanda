import json
from dataclasses import dataclass

@dataclass
class Ride:
    lpep_pickup_datetime: str
    PULocationID: int
    DOLocationID: int
    trip_distance: float
    total_amount: float

def ride_from_row(row):
    return Ride(
        lpep_pickup_datetime=str(row['lpep_pickup_datetime']),
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        trip_distance=float(row['trip_distance']),
        total_amount=float(row['total_amount']),
    )


def ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return Ride(**ride_dict)