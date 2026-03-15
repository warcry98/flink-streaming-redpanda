import dataclasses
import sys
import time
from pathlib import Path
import urllib.request

import orjson
import pyarrow.parquet as pq
from kafka import KafkaProducer

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Ride, safe_optional_int


URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"
LOCAL_FILE = "green_tripdata_2025-10.parquet"

COLUMNS = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "passenger_count",
    "trip_distance",
    "tip_amount",
    "total_amount",
]

BOOTSTRAP_SERVER = "localhost:9092"
TOPIC = "green-trips"


def ride_serializer(ride: Ride):
    return orjson.dumps(dataclasses.asdict(ride))


def download_if_needed():
    if not Path(LOCAL_FILE).exists():
        print("Downloading parquet file...")
        urllib.request.urlretrieve(URL, LOCAL_FILE)
        print("Download finished")


producer = KafkaProducer(
    bootstrap_servers=[BOOTSTRAP_SERVER],
    value_serializer=ride_serializer,
    linger_ms=50,
    batch_size=131072,
    compression_type="gzip",
)


def process_batch(batch):

    cols = {name: batch[name].to_pylist() for name in COLUMNS}
    size = len(cols["PULocationID"])

    for i in range(size):

        ride = Ride(
            lpep_pickup_datetime=str(cols["lpep_pickup_datetime"][i]),
            lpep_dropoff_datetime=str(cols["lpep_dropoff_datetime"][i]),
            PULocationID=int(cols["PULocationID"][i]),
            DOLocationID=int(cols["DOLocationID"][i]),
            passenger_count=safe_optional_int(cols["passenger_count"][i]),
            trip_distance=float(cols["trip_distance"][i]),
            tip_amount=float(cols["tip_amount"][i]),
            total_amount=float(cols["total_amount"][i]),
        )

        producer.send(TOPIC, value=ride)


if __name__ == "__main__":

    t0 = time.time()

    download_if_needed()

    print("Streaming parquet with PyArrow...")

    parquet_file = pq.ParquetFile(LOCAL_FILE)

    for batch in parquet_file.iter_batches(columns=COLUMNS, batch_size=50000):
        process_batch(batch)

    producer.flush()

    t1 = time.time()

    print(f"Finished in {(t1 - t0):.2f} seconds")
