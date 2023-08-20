from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
from time import sleep

# You can generate an API token from the "API Tokens Tab" in the UI
token = "3Ey6Ez4bMufkeF2Bd5BGcmgu4jQMyBSska__RN2AWc8tdZ16wFSiMVr3ltrZSiBKT9kjXY7NRa09v33qzHaLsw=="
org = "org"
bucket = "bucket"
try:
    with InfluxDBClient(url="http://10.0.0.130:8086", token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        data = "mem,host=host1 used_percent={}".format(np.random.randint(0, 100))
        write_api.write(bucket, org, data)

        client.close()
except:
    print("error")
