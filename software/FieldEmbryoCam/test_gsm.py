import tsys01
#from time import sleep
from datetime import datetime
from serial import Serial
import time
import numpy as np
import math


def transmit_package(package):
        gsm.flushInput()
        ts1 = time.time()
        package_length = len(package)
        transmit = 'AT+SMPUB="v1/devices/me/telemetry",' + str(package_length) + ', 1,1'
        gsm.write(str.encode(transmit + '\r\n'))
        print(str(gsm.read_until('OK')))
        transmit = package
        gsm.write(str.encode(transmit + '\r'))
        print(str(gsm.read_until('OK')))         
        ts2 = time.time()
        print('[INFO]: Took ' + str(ts2-ts1) + ' seconds')
        time.sleep(0.4)
        
gsm = Serial('/dev/ttyAMA0', 57600)
gsm.timeout=3
gsm.flushInput()
gsm.write(str.encode('ATE1'+ '\r'))
print(str(gsm.read_until('OK\r')))
print('[INFO]: Setting up GSM')
transmit = "AT+CFUN=1" # Reset
gsm.flushInput()
gsm.write(str.encode(transmit + '\r\n')) 
time.sleep(2)
print(str(gsm.read_until('OK\r\n')))
# Hard reset
#transmit = "AT+CFUN=1,1"
#gsm.write(str.encode(transmit + '\r\n')) 
#time.sleep(5)
#print(str(gsm.read_until('OK\r\n')))
#transmit = "ATE0"
#gsm.write(str.encode(transmit + '\r')) 
#time.sleep(2)
#print(str(gsm.read_until('OK\r')))
transmit = 'AT+CNACT=1, "data.uk"'
gsm.write(str.encode(transmit + '\r\n'))
print(str(gsm.read_until('OK\r\n')))
transmit = 'AT+SMCONF="URL", "thingsboard.cloud","1883"'
gsm.write(str.encode(transmit + '\r\n'))
print(str(gsm.read_until('OK\r\n')))
transmit = 'AT+SMCONF="USERNAME", "otills"'
gsm.write(str.encode(transmit + '\r\n'))
print(str(gsm.read_until('OK\r\n')))
transmit = 'AT+SMCONF="PASSWORD", "ottowa"'
gsm.write(str.encode(transmit + '\r\n'))
print(str(gsm.read_until('OK\r\n')))
transmit = 'AT+SMCONF="TOPIC", "/v1/devices/me/telemetry"'
gsm.write(str.encode(transmit + '\r\n'))
print(str(gsm.read_until('OK\r\n')))
transmit = 'AT+SMCONF="KEEPTIME", "60"'
gsm.write(str.encode(transmit + '\r\n'))
print(str(gsm.read_until('OK\r')))
transmit = 'AT+SMCONN'
gsm.write(str.encode(transmit + '\r\n'))
print(str(gsm.read_until('OK\r')))
package = {}
transmit_package("{"f"'temperature':'55.5'" + "}")
#print("[INFO]: Transmitting - {"f"'{key}':'{package}'" + "}")
