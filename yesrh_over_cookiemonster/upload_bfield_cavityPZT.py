#
# Copyright (C) 2018 Pico Technology Ltd. See LICENSE file for terms.
#
# PS4824 BLOCK MODE EXAMPLE
# This example opens a 4000a driver device, sets up two channels and a trigger then collects a block of data.
# This data is then plotted as mV against time in ns.

import ctypes
import numpy as np
from picosdk.ps4000a import ps4000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok


from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
from time import sleep
import os
import sys
# add current directory to the path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import db_credential

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open 4000 series PicoScope
# Returns handle to chandle for use in future API functions
status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(chandle), None)

try:
    assert_pico_ok(status["openunit"])
except:

    powerStatus = status["openunit"]

    if powerStatus == 286:
        status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
    else:
        raise

    assert_pico_ok(status["changePowerSource"])

# Set up channel A
# handle = chandle
# channel = PS4000a_CHANNEL_A = 0
# enabled = 1
# coupling type = PS4000a_DC = 1
# range = PS4000a_2V = 7
# analogOffset = 0 V
chARange = 9
status["setChA"] = ps.ps4000aSetChannel(chandle, 0, 1, 1, chARange, 0)
assert_pico_ok(status["setChA"])

chBRange = 9
status["setChB"] = ps.ps4000aSetChannel(chandle, 1, 1, 1, chBRange, 0)
assert_pico_ok(status["setChB"])

chCRange = 9
status["setChC"] = ps.ps4000aSetChannel(chandle, 2, 1, 1, chCRange, 0)
assert_pico_ok(status["setChC"])

chDRange = 9
status["setChD"] = ps.ps4000aSetChannel(chandle, 3, 1, 1, chDRange, 0)
assert_pico_ok(status["setChD"])

chERange = 9
status["setChE"] = ps.ps4000aSetChannel(chandle, 4, 1, 1, chERange, 0)
assert_pico_ok(status["setChE"])

chFRange = 9
status["setChF"] = ps.ps4000aSetChannel(chandle, 5, 1, 1, chFRange, 0)
assert_pico_ok(status["setChF"])

chGRange = 9
status["setChG"] = ps.ps4000aSetChannel(chandle, 6, 1, 1, chGRange, 0)
assert_pico_ok(status["setChG"])

chHRange = 9
status["setChH"] = ps.ps4000aSetChannel(chandle, 7, 1, 1, chHRange, 0)
assert_pico_ok(status["setChH"])

# Set up single trigger
# handle = chandle
# enabled = 1
# source = PS4000a_CHANNEL_A = 0
# threshold = 1024 ADC counts
# direction = PS4000a_RISING = 2
# delay = 0 s
# auto Trigger = 1000 ms
status["trigger"] = ps.ps4000aSetSimpleTrigger(chandle, 1, 0, 1024, 2, 0, 10)
assert_pico_ok(status["trigger"])

# Set number of pre and post trigger samples to be collected
preTriggerSamples = 5000
postTriggerSamples = 5000
maxSamples = preTriggerSamples + postTriggerSamples

# Get timebase information
# WARNING: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
# To access these Timebases, set any unused analogue channels to off.
# handle = chandle
# timebase = 8 = timebase
# noSamples = maxSamples
# pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
# pointer to maxSamples = ctypes.byref(returnedMaxSamples)
# segment index = 0
timebase = 1000
timeIntervalns = ctypes.c_float()
returnedMaxSamples = ctypes.c_int32()
oversample = ctypes.c_int16(1)
status["getTimebase2"] = ps.ps4000aGetTimebase2(chandle, timebase, maxSamples, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
assert_pico_ok(status["getTimebase2"])

# Run block capture
# handle = chandle
# number of pre-trigger samples = preTriggerSamples
# number of post-trigger samples = PostTriggerSamples
# timebase = 3 = 80 ns = timebase (see Programmer's guide for mre information on timebases)
# time indisposed ms = None (not needed in the example)
# segment index = 0
# lpReady = None (using ps4000aIsReady rather than ps4000aBlockReady)
# pParameter = None
status["runBlock"] = ps.ps4000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, None, 0, None, None)
assert_pico_ok(status["runBlock"])

# Check for data collection to finish using ps4000aIsReady
ready = ctypes.c_int16(0)
check = ctypes.c_int16(0)
while ready.value == check.value:
    status["isReady"] = ps.ps4000aIsReady(chandle, ctypes.byref(ready))

# Create buffers ready for assigning pointers for data collection
bufferEMax = (ctypes.c_int16 * maxSamples)()
bufferFMax = (ctypes.c_int16 * maxSamples)()
bufferGMax = (ctypes.c_int16 * maxSamples)()
bufferHMax = (ctypes.c_int16 * maxSamples)()

# Set data buffer location for data collection from channel A
# handle = chandle
# source = PS4000a_CHANNEL_A = 0
# pointer to buffer max = ctypes.byref(bufferAMax)
# pointer to buffer min = ctypes.byref(bufferAMin)
# buffer length = maxSamples
# segementIndex = 0
# mode = PS4000A_RATIO_MODE_NONE = 0
status["setDataBuffersE"] = ps.ps4000aSetDataBuffers(chandle, 4, ctypes.byref(bufferEMax), ctypes.byref(bufferEMax), maxSamples, 0 , 0)
assert_pico_ok(status["setDataBuffersE"])

status["setDataBuffersF"] = ps.ps4000aSetDataBuffers(chandle, 5, ctypes.byref(bufferFMax), ctypes.byref(bufferFMax), maxSamples, 0 , 0)
assert_pico_ok(status["setDataBuffersF"])

status["setDataBuffersG"] = ps.ps4000aSetDataBuffers(chandle, 6, ctypes.byref(bufferGMax), ctypes.byref(bufferGMax), maxSamples, 0 , 0)
assert_pico_ok(status["setDataBuffersG"])

status["setDataBuffersH"] = ps.ps4000aSetDataBuffers(chandle, 7, ctypes.byref(bufferHMax), ctypes.byref(bufferHMax), maxSamples, 0 , 0)
assert_pico_ok(status["setDataBuffersH"])

# create overflow loaction
overflow = ctypes.c_int16()
# create converted type maxSamples
cmaxSamples = ctypes.c_int32(maxSamples)

# Retried data from scope to buffers assigned above
# handle = chandle
# start index = 0
# pointer to number of samples = ctypes.byref(cmaxSamples)
# downsample ratio = 0
# downsample ratio mode = PS4000a_RATIO_MODE_NONE
# pointer to overflow = ctypes.byref(overflow))
status["getValues"] = ps.ps4000aGetValues(chandle, 0, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
assert_pico_ok(status["getValues"])


# find maximum ADC count value
# handle = chandle
# pointer to value = ctypes.byref(maxADC)
maxADC = ctypes.c_int16(32767)

# convert ADC counts data to mV
adc2mVChEMax =  adc2mV(bufferEMax, chERange, maxADC)
adc2mVChFMax =  adc2mV(bufferFMax, chFRange, maxADC)
adc2mVChGMax =  adc2mV(bufferGMax, chGRange, maxADC)
adc2mVChHMax =  adc2mV(bufferHMax, chHRange, maxADC)

# Create time data
time = np.linspace(0, (cmaxSamples.value - 1) * timeIntervalns.value, cmaxSamples.value)

# Stop the scope
# handle = chandle
status["stop"] = ps.ps4000aStop(chandle)
assert_pico_ok(status["stop"])

# Close unitDisconnect the scope
# handle = chandle
status["close"] = ps.ps4000aCloseUnit(chandle)
assert_pico_ok(status["close"])

chE_mean = np.mean(adc2mVChEMax)
chF_mean = np.mean(adc2mVChFMax)
chG_mean = np.mean(adc2mVChGMax)
chH_mean = np.mean(adc2mVChHMax)

chE_std = np.std(adc2mVChEMax)
chF_std = np.std(adc2mVChFMax)
chG_std = np.std(adc2mVChGMax)
chH_std = np.std(adc2mVChHMax)


token = db_credential.token
org = db_credential.org
bucket = db_credential.bucket
url = db_credential.url
with InfluxDBClient(url=url, token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    messages = [
        f"pico4824A,channel=E_cavPZT mean[mV]={chE_mean}",
        f"pico4824A,channel=F_Bx mean[mV]={chF_mean}",
        f"pico4824A,channel=G_By mean[mV]={chG_mean}",
        f"pico4824A,channel=H_Bz mean[mV]={chH_mean}",
        f"pico4824A,channel=E_cavPZT std[mV]={chE_std}",
        f"pico4824A,channel=F_Bx std[mV]={chF_std}",
        f"pico4824A,channel=G_By std[mV]={chG_std}",
        f"pico4824A,channel=H_Bz std[mV]={chH_std}"
        ]
    for message in messages:
        print(message)
        write_api.write(bucket, org, message)
    client.close()


# # plot data from channel A and B
plt.plot(time, adc2mVChEMax[:], label="E")
plt.plot(time, adc2mVChFMax[:], label="F")
plt.plot(time, adc2mVChGMax[:], label="G")
plt.plot(time, adc2mVChHMax[:], label="H")
plt.legend()
plt.xlabel('Time (ns)')
plt.ylabel('Voltage (mV)')
plt.show()

# display status returns
print(status)