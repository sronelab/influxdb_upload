from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
from time import sleep

# You can generate an API token from the "API Tokens Tab" in the UI
token = "my-token"
org = "my-org"
bucket = "my-bucket"

for i in range(0, 10000):
    with InfluxDBClient(url="http://10.0.0.130:8086", token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        data = "mem,host=host1 used_percent={}".format(np.random.randint(0, 100))
        write_api.write(bucket, org, data)

        # query = 'from(bucket: "my-bucket") |> range(start: -1h)'
        # tables = client.query_api().query(query, org=org)
        # for table in tables:
        #     for record in table.records:
        #         print(record)

        client.close()

    sleep(5)
    print(data)
