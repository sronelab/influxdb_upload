#
# Copyright (C) 2018-2022 Pico Technology Ltd. See LICENSE file for terms.
#
# PS3000A BLOCK MODE EXAMPLE
# This example opens a 3000a driver device, sets up two channels and a trigger then collects a block of data.
# This data is then plotted as mV against time in ns.

import ctypes
import numpy as np
from picosdk.ps3000a import ps3000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
from time import sleep

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
token = "yelabtoken"
org = "yelab"
bucket = "quiet_room"

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open 5000 series PicoScope
resolution =ps.PS3000A_DEVICE_RESOLUTION["PS3000A_DR_14BIT"]
# Returns handle to chandle for use in future API functions
status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(chandle), None, resolution)

try:
    assert_pico_ok(status["openunit"])
except: # PicoNotOkError:

    powerStatus = status["openunit"]

    if powerStatus == 286:
        status["changePowerSource"] = ps.ps3000aChangePowerSource(chandle, powerStatus)
    elif powerStatus == 282:
        status["changePowerSource"] = ps.ps3000aChangePowerSource(chandle, powerStatus)
    else:
        raise

    assert_pico_ok(status["changePowerSource"])

# Set up channels
channel_names = ["A", "B", "C", "D"]
channel_labels = ["MJM_int_V_con", "prestab_PDHPD_DC", "ECDL_PZT_servo_in", "prestab_PZT_servo_in"]
for channel_name in channel_names:
    # handle = chandle
    channel = ps.PS3000A_CHANNEL[f"PS3000A_CHANNEL_{channel_name}"]
    # enabled = 1
    coupling_type = ps.PS3000A_COUPLING["PS3000A_DC"]
    chARange = ps.PS3000A_RANGE["PS3000A_2V"]
    # analogue offset = 0 V
    status[f"setCh{channel_name}"] = ps.ps3000aSetChannel(chandle, channel, 1, coupling_type, chARange, 0)
    assert_pico_ok(status[f"setCh{channel_name}"])

# find maximum ADC count value
# handle = chandle
# pointer to value = ctypes.byref(maxADC)
maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps3000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])

# Set up single trigger
# handle = chandle
# enabled = 1
source = ps.PS3000A_CHANNEL["PS3000A_CHANNEL_A"]
threshold = int(mV2adc(500,chARange, maxADC))
# direction = PS3000A_RISING = 2
# delay = 0 s
# auto Trigger = 1000 ms
status["trigger"] = ps.ps3000aSetSimpleTrigger(chandle, 1, source, threshold, 2, 0, 1000)
assert_pico_ok(status["trigger"])

# Set number of pre and post trigger samples to be collected
preTriggerSamples = 2500
postTriggerSamples = 2500
maxSamples = preTriggerSamples + postTriggerSamples

# Get timebase information
# Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
# To access these Timebases, set any unused analogue channels to off.
# handle = chandle
timebase = 2**5
# noSamples = maxSamples
# pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
# pointer to maxSamples = ctypes.byref(returnedMaxSamples)
# segment index = 0
timeIntervalns = ctypes.c_float()
returnedMaxSamples = ctypes.c_int32()
status["getTimebase2"] = ps.ps3000aGetTimebase2(chandle, timebase, maxSamples, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
assert_pico_ok(status["getTimebase2"])


# Create buffers ready for assigning pointers for data collection
buffer = {}
buffer["bufferAMax"] = (ctypes.c_int16 * maxSamples)()
buffer["bufferAMin"] = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example
buffer["bufferBMax"] = (ctypes.c_int16 * maxSamples)()
buffer["bufferBMin"] = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example
buffer["bufferCMax"] = (ctypes.c_int16 * maxSamples)()
buffer["bufferCMin"] = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example
buffer["bufferDMax"] = (ctypes.c_int16 * maxSamples)()
buffer["bufferDMin"] = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example

# Set data buffer location for data collection from channel A
for channel_name in channel_names:
    source = ps.PS3000A_CHANNEL[f"PS3000A_CHANNEL_{channel_name}"]
    # pointer to buffer max = ctypes.byref(bufferAMax)
    # pointer to buffer min = ctypes.byref(bufferAMin)
    # buffer length = maxSamples
    # segment index = 0
    # ratio mode = PS3000A_RATIO_MODE_NONE = 0
    status[f"setDataBuffers{channel_name}"] = ps.ps3000aSetDataBuffers(chandle, source, ctypes.byref(buffer[f"buffer{channel_name}Max"]), ctypes.byref(buffer[f"buffer{channel_name}Min"]), maxSamples, 0, 0)
    assert_pico_ok(status[f"setDataBuffers{channel_name}"])

for ii in range(100):
    
    # Run block capture
    # handle = chandle
    # number of pre-trigger samples = preTriggerSamples
    # number of post-trigger samples = PostTriggerSamples
    # timebase = 8 = 80 ns (see Programmer's guide for mre information on timebases)
    # time indisposed ms = None (not needed in the example)
    # segment index = 0
    # lpReady = None (using ps3000aIsReady rather than ps3000aBlockReady)
    # pParameter = None
    status["runBlock"] = ps.ps3000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, None, 0, None, None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps3000aIsReady
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps3000aIsReady(chandle, ctypes.byref(ready))

    # create overflow loaction
    overflow = ctypes.c_int16()
    # create converted type maxSamples
    cmaxSamples = ctypes.c_int32(maxSamples)

    # Retried data from scope to buffers assigned above
    # handle = chandle
    # start index = 0
    # pointer to number of samples = ctypes.byref(cmaxSamples)
    # downsample ratio = 0
    # downsample ratio mode = PS3000A_RATIO_MODE_NONE
    # pointer to overflow = ctypes.byref(overflow))
    status["getValues"] = ps.ps3000aGetValues(chandle, 0, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])

    # convert ADC counts data to mV
    data = {}
    for channel_name in channel_names:
        data[f"CH{channel_name}"] = adc2mV(buffer[f"buffer{channel_name}Max"], chARange, maxADC)
    print(data)

    with InfluxDBClient(url="http://yesnuffleupagus.colorado.edu:8086/", token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for ii in range(len(channel_names)):
            data_to_save = data[f"data{channel_names[ii]}"]
            write_api.write(bucket, org, f"MJM,Channel={channel_labels[ii]} data[mV]={data_to_save}")
    
    sleep(10)


# Stop the scope
status["stop"] = ps.ps3000aStop(chandle)
assert_pico_ok(status["stop"])

# Close unit Disconnect the scope
status["close"]=ps.ps3000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# display status returns
print(status)