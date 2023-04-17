import tsys01
#from time import sleep
from datetime import datetime
from serial import Serial
import time
import numpy as np
import math

class GSM():
    def __init__(self, mode='mqtt'):
        self.mode = mode
        if mode == 'mqtt':
            self.gsm = Serial('/dev/ttyAMA0', 57600)
        else:
            self.gsm = Serial('/dev/ttyS0', 57600)
        self.gsm.timeout=2.5
        self.gsm.flushInput()
        #AT+SAPBR=1,1,"OK",5000
        #AT+SAPBR=2,1,"OK",5000
    
    def initiate_gsm(self, access_token):
        # Access token only enabled for mqtt - not email or websocket.
        if self.mode == 'email':
            pipeline = {
            1:'AT+CGATT=1',
            2:'ATE1',
            3:'AT+SAPBR=3,1,"CONTYPE","GPRS"',
            4:'AT+SAPBR=3,1,"APN","data.uk"',
            5:'AT+SAPBR=3,1,"USER","user"',
            6:'AT+SAPBR=3,1,"PWD","one2one"',
            7:'AT+SAPBR=1,1',
            8:'AT+EMAILCID=1',
            9:'AT+EMAILTO=60',
            10:'AT+EMAILSSL=1',
            11:'AT+SMTPSRV="smtp.gmail.com",465',
            12:'AT+SMTPAUTH=1,"olitills@gmail.com","radixBalthica"',
            13:'AT+SMTPFROM="olitills@gmail.com","Oli Tills"',
            14:'AT+SMTPRCPT=0,0,"trigger@applet.ifttt.com"," "'
            }
            self.gsm.flushInput()
            for f in range(1, len(pipeline)):
               self.send_command(pipeline[f])
        if self.mode == 'websocket':
            pipeline = {
            1:'AT+CGATT=1',
            2:'ATE1',
            3:'AT+SAPBR=3,1,"CONTYPE","GPRS"',
            4:'AT+SAPBR=3,1,"APN","data.uk"',
            5:'AT+SAPBR=3,1,"USER","user"',
            6:'AT+SAPBR=3,1,"PWD","one2one"',
            7:'AT+SAPBR=1,1',
            8:'AT+EMAILCID=1',
            9:'AT+EMAILTO=60',
            10:'AT+EMAILSSL=1'
            }
            for f in range(1, len(pipeline)):
                self.send_command(pipeline[f])
            # Setup websocket - still to be included - not tested..
            self.gsm.write(str.encode('AT+HTTPPARA="CID",1' + '\r'))
            print(str(self.gsm.read_until('OK\r\n')))            
            self.gsm.write(str.encode('AT+HTTPPARA="URL","https://io.adafruit.com/api/v2/webhooks/feed/TY5rpSZpazJZvcUo3XJP9xfKQFtb/raw"' + '\r'))
            print(str(self.gsm.read_until('OK\r\n')))
            
        if self.mode == 'mqtt':
            pipeline = {
            1:'AT+CFUN=1,1',
            2:'ATE1',
            3:'AT+CNACT=1, "iot.1nce.net"',
            4:'AT+SMCONF="URL","thingsboard.cloud","1883"',
            5:'AT+SMCONF="KEEPTIME","60"',
            6:'AT+SMCONF="USERNAME","%s"' %access_token,
            #6:'AT+SMCONF="USERNAME","otills"',
            #7:'AT+SMCONF="PASSWORD","ottowa"',
            7:'AT+SMCONF="TOPIC","v1/devices/me/telemetry"',
            8:'AT+SMCONN'
            }
            self.gsm.flushInput()
            for f in range(1, len(pipeline)+1):
                self.send_command(pipeline[f])
    
    def send_command(self, command):
        #self.gsm.timeout=2
        msg = command + '\r\n'
        print('[INFO]: Sending ' + msg)
        self.gsm.write(str.encode(msg))
        rcvd = self.gsm.read_until('OK\r\n')
        print('[INFO]: Response from first attempt at sending ' + str(msg))
        print(str(rcvd))
        if 'OK' not in str(rcvd):
            self.gsm.flushInput()
            print('[INFO]: Second attempt at sending ', msg)
            self.gsm.write(str.encode(msg))
            rcvd = self.gsm.read_until('OK\r\n')
        if 'OK' not in str(rcvd):
            self.gsm.flushInput()
            print('[INFO]: Third attempt at sending ', msg)
            self.gsm.write(str.encode(msg))
            rcvd = self.gsm.read_until('OK\r\n')
            self.gsm.flushInput()
        
    def send_data(self,key, package):
        #
        if self.mode == 'email':
            self.gsm.write(str.encode('AT+SMTPSUB=' + key + '\r'))
            print(str(self.gsm.read_until('OK\r')))
            package_len = len(str(package))
            self.gsm.write(str.encode('AT+SMTPBODY=' + str(package_len) + '\r'))
            print(str(self.gsm.read_until('OK\r\n')))
            self.gsm.write(str.encode(str(package) +'\r'))
            print(str(self.gsm.read_until('OK\r\n')))
            self.gsm.write(str.encode('AT+SMTPSEND' + '\r'))
            print(str(self.gsm.read_until('SMTPSEND:')))
            time.sleep(10)
            print('bytes waiting...' + str(self.gsm.in_waiting))
            print(self.gsm.read_until(size=self.gsm.in_waiting))
        if self.mode == 'websocket':
            self.gsm.write(str.encode('AT+SMTPSRV="smtp.gmail.com",465' + '\r'))
            print(str(self.gsm.read_until('OK\r\n')))
        if self.mode == 'mqtt':
            #self.gsm.timeout=1.25
            self.transmit_data("{"f"'{key}':'{package}'" + "}")
            print("[INFO]: Transmitting - {"f"'{key}':'{package}'" + "}")
    
    def split_and_send_thumbnail(self,
                                 data,
                                 header = 'data:image/png;base64,',
                                 max_size= 450):
        #header = 'thumbnail:data:image/png;base64,',
        #self.gsm.timeout=3
        self.gsm.flushInput()
        tsend1 = time.time()
        self.transmit_data("{'clear_thumbnail':''}")
        self.transmit_data("{'new_thumbnail':''}")
        package_size = math.ceil(len(data)/max_size)
        bins = np.arange(0, len(data),max_size)
        bins = np.append(bins, len(data))
        print('Bins: ' + str(bins))
        for i in range(len(bins)-1):
            print('[INFO]: Sending packet ' + str(i) + '/' + str(len(bins)-1) + ' of image')
            if i ==0:
                package = header + data[bins[i]:bins[i+1]]
                package = "{'thumbnail': " + f"'{package}'" + "}"
                self.transmit_data(package)
                #time.sleep(0.4)                     
            else:
                package = "{'thumbnail': " + f"'{data[bins[i]:bins[i+1]]}'" + "}"
                self.transmit_data(package)
                #time.sleep(0.4)
                
            print(str(self.gsm.out_waiting))
            print(str(package))
            #time.sleep(0.4)
        print('[INFO]: Closing thumbnail transmission')
        self.transmit_data("{'thumbnail':'', 'close_thumbnail':''}")
        tsend2 = time.time()
        print('[INFO]: Thumbnail transmission time: ' + str(round(tsend2-tsend1,2)) + ' seconds')
        #time.sleep(0.5)

    def transmit_data(self,package):
        self.gsm.flushInput()
        #self.gsm.timeout=1.25
        ts1 = time.time()
        package_length = len(package)
        #SMTPSUB
        transmit = 'AT+SMPUB="v1/devices/me/telemetry",' + str(package_length) + ', 1,1'
        print('Sending: ' + str(transmit))
        self.gsm.write(str.encode(transmit + '\r\n'))
        print(str(self.gsm.read_until('OK')))
        transmit = package
        self.gsm.write(str.encode(transmit + '\r\n'))
        print(str(self.gsm.read_until('OK')))
        ts2 = time.time()
        print('[INFO]: Took ' + str(ts2-ts1) + ' seconds')
        time.sleep(0.4)                           
