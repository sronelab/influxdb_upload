import sys
import datetime
import pyvisa
import time
import os
import pandas as pd
import numpy as np
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

DATA_FOLDER = "data"

"""loging data"""
def log_data(delay=0.1):
    DATA_DIR = os.path.join(DATA_FOLDER, "{}.csv".format(str(datetime.datetime.today().date())))
    rm = pyvisa.ResourceManager()
    # print(rm.list_resources())
    inst = rm.open_resource('ASRL4::INSTR')
    inst.baud_rate=19200
    # print(inst.query("*IDN?", delay=delay))
    inst.query("*IDN?", delay=delay)
    data = {}
    for ii in [4, 5, 6]:
        inst.write(":SLOT {}".format(ii))
        # print(inst.query(":SLOT?", delay=delay))
        data["I_{}".format(ii)] = float(inst.query(":ILD:SET?", delay=delay).split(" ")[-1])
        data["P_{}".format(ii)] = float(inst.query(":POPT:ACT?", delay=delay).split(" ")[-1])

    inst.write("&GTL")

    df = pd.DataFrame(data, index = [datetime.datetime.now()])
    df.index.name = "time"
    if os.path.exists(DATA_DIR):
        df.to_csv(DATA_DIR, header=False, mode="a+")
    else:
        df.to_csv(DATA_DIR, mode="a")

    # Sending data to the database on yesnuffleupagus.colorado.edu:8086
    # https://powersj.io/posts/influxdb-client-python-write-api-deep-dive/

        # Influxdb info
    token = 'yelabtoken'
    org = 'yelab'
    bucket = 'data_logging'

    df.index = pd.to_datetime(df.index, unit='s')

    records=[
        {
            "measurement": "Blues",
            "tags": {"Name": k},
            "fields": {"Value": v},
            "time": datetime.datetime.now()
        }
        for k, v in data.items()
    ]
    print(records)

    with InfluxDBClient(url="http://yesnuffleupagus.colorado.edu:8086", token=token, org=org, debug=False) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for k, v in data.items():
            write_api.write(bucket, org, "Blues,Channel={} Value={}".format(k, v))
        client.close()
    print(df)


"""Main loop"""
if __name__ == "__main__":
    try:
        while True:
            try:
                log_data()
            except pyvisa.errors.VisaIOError:
                print("VISA Error detected.")
            time.sleep(5)
    except KeyboardInterrupt:
        pass    


