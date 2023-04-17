import acquisition
import analysis
import env_sensors
import display
import sys
import gsm
import glob
from datetime import datetime
import json
import os
import cv2
import io
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import time as time
#from Adafruit_IO import Client, Feed
import pickle
import RPi.GPIO as GPIO
from pijuice import PiJuice

class Deployment:
    def __init__(self):
        #  Turn wifi off to reduce power consumtion
        os.system('sudo ifconfig wlan0 down')
        #self.kill = kill_switch
        # Instantiate PiJuice interface object
        self.pijuice = PiJuice(1, 0x14)
        #  Print time for diagnostic purposes
        rtc_now = self.pijuice.rtcAlarm.GetTime()
        print('[INFO]: Date: ' + str(rtc_now['data']['year']) + '-' + str(rtc_now['data']['month']) + '-' + str(rtc_now['data']['day']))
        print('[INFO]: Time: ' + str(rtc_now['data']['hour']) + ':' + str(rtc_now['data']['minute']) + ':' + str(rtc_now['data']['second']))

        #  Set a timeout limit in minutes - assumes crash if no signal detected.
        self.pijuice.power.SetWatchdog(5)
        self.tm_out = self.pijuice.power.GetWatchdog()
        print('[INFO]: Timeout limit: ' + str(self.tm_out['data']) + ' mins')

        #  Set pin reference tp physical pin number for ease of use
        GPIO.setmode(GPIO.BOARD)

        #  Set desired channel and define as an output
        self.LED_pin = 22
        GPIO.setup(self.LED_pin, GPIO.OUT)

        self.data_acquisition_pipeline = {
                               1: self.load_config, 
                               2: self.initiate_results,
                               3: self.get_battery,
                               4: self.query_environmental_sensors,
                               5: self.acquire,
                               6: self.produce_thumbnail,
                               7: self.save_data,
                               8: self.send_via_gsm,
                               9: self.print_battery,
                               #10: self.update_display,
                               10: self.close
                            }
        self.next_in_pipeline = 1

    def get_battery(self):
        #  Transmits battery level at beginning of acquisition cycle.
        # Battery status and RTC timestamp
        #self.rtc_now = pijuice.rtcAlarm.GetTime()
        #print('Date: ' + str(rtc_now['data']['year']) + '-' + str(rtc_now['data']['month']) + '-' + str(rtc_now['data']['day']))
        #print('Time: isition_pipeline[f]()
        self.batt_pct = self.pijuice.status.GetChargeLevel()
        self.generated_data['battery'] = str(self.batt_pct['data'])
        print('Batt. charge: ' + str(self.generated_data['battery']) + ' %')
        self.batt_vlt = self.pijuice.status.GetBatteryVoltage()
        self.generated_data['voltage'] = str(round(float(self.batt_vlt['data'])/1000,2))
        print('Batt. voltage: ' + str(self.generated_data['voltage']) + ' V')
        
    def print_battery(self): 
        #  Prints battery level after data transmission.
        #  Doesn't save to file.
        rtc_now = self.pijuice.rtcAlarm.GetTime()
        self.batt_pct = self.pijuice.status.GetChargeLevel()
        self.batt_vlt = self.pijuice.status.GetBatteryVoltage()
        print('[INFO]: Date: ' + str(rtc_now['data']['year']) + '-' + str(rtc_now['data']['month']) + '-' + str(rtc_now['data']['day']))
        print('[INFO]: Time: ' + str(rtc_now['data']['hour']) + ':' + str(rtc_now['data']['minute']) + ':' + str(rtc_now['data']['second']))
        print('[INFO]: Post-transmission battery charge: ' + str(self.batt_pct['data']) + ' %')        
        print('[INFO]: Post-transmission battery voltage: ' + str(round(float(self.batt_vlt['data'])/1000,2)) + 'V')
    
    def query_environmental_sensors(self):
        # Collect environmental data
        for sensor in self.config['env_sensors']:
            active_sensor = env_sensors.Sensor(str(sensor))
            active_sensor.initialise()
            self.generated_data[str(sensor)] = str(active_sensor.readSensor())
        print(self.generated_data)
    
    def acquire(self):
        if self.config["acq_duration"] > 0:
            #try: # Incomplete try block, this will raise a syntax error
            GPIO.output(self.LED_pin, GPIO.HIGH)
            # Allow the LED ring to lightup..
            time.sleep(10)
            active_cam = acquisition.Acquisition()
            active_cam.initialise_cam()
            os.makedirs(self.config['acq_path'] + self.timestamp + '/')
            self.active_path = self.config['acq_path'] + self.timestamp + '/'
            n = self.config['acq_duration']*self.config['acq_framerate']
            self.generated_data['n'] = n
            print('Acquiring sequence')
            self.generated_data['acq_path'] = self.active_path
            active_cam.acquire_seq(n, self.active_path)
            active_cam.close()
                #  Signal LED module OFF
            GPIO.output(self.LED_pin, GPIO.LOW)
        else:
            print('[INFO] Camera connection issue')
            active_cam.close()
            
    def load_config(self):
        # Load config
        with open('./config.json', 'r') as cfg:
            self.config = json.load(cfg)
        
    def calculate_epts(self):
        mpx = []
        for i in range(int(generated_data['n'])):
        #for i in range(300):
            #mpx.append(np.mean(cv2.imread(self.active_path +'img_' + str(i).zfill(3) + '.jpg')))
            mpx.append(np.mean(cv2.imread(self.generated_data['acq_path'] +'img_' + str(i).zfill(3) + '.jpg')))
        self.generated_data['mpx'] = mpx
        print('EPTs still to be implemented, but mpx being saved..')
        #epts = analysis.Analysis('/home/pi/Desktop/imseq/2021_08_20_21_51_57/', 1)
        #generated_data['epts'] = epts.calculate_epts()
        
    def initiate_results(self):
        self.generated_data = dict()
        rtc_now = self.pijuice.rtcAlarm.GetTime()
        self.timestamp = str(rtc_now['data']['year']) + '_' + str(rtc_now['data']['month']) + '_' + str(rtc_now['data']['day']) + '_' + str(rtc_now['data']['hour']) + '_' + str(rtc_now['data']['minute']) + '_' + str(rtc_now['data']['second'])

        #self.timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.generated_data['datetime'] = self.timestamp

    def send_via_gsm(self): 
        if self.config['gsm_active']:
            print('Initiating GSM')
            network = gsm.GSM()
            network.initiate_gsm(self.config["device_id"])
            for key, value in self.generated_data.items():
                print('key = ' + str(key))
                print('value = ' + str(value))
                if ((key == 'temperature') or (key == 'pressure') or (key == 'battery')):
                    print('[INFO]: Sending: ', str(round(float(value),2)))
                    network.send_data(key,round(float(value),2))
                if (key =='image'):
                    print('[INFO]: Splitting and sending image')
                    network.split_and_send_thumbnail(self.generated_data['image'])
                    #network.send_data('image', generated_data['image'])
    
    def produce_thumbnail(self):
        # GSM image
        if self.config["gsm_image"]:
            print('[INFO]: Formatting image for GSM transmission')
            tmp = cv2.imread(self.active_path + 'img_000.jpg')
            thumb = cv2.resize(tmp, (50,50), cv2.INTER_NEAREST)
            cv2.imwrite(self.active_path + 'thumbnail.jpg', thumb)
            self.generated_data['thumbnail'] = [thumb]
            image = Image.fromarray(self.generated_data['thumbnail'][0])
            stream = io.BytesIO()
            image.save(stream,format='png', quality=30,optimize=True)
            stream.seek(0)
            value = base64.b64encode(stream.read())
            print(value)
            print(str(value))

            print('LENGTH:' + str(len(value)))
            #cv2.imencode('.jpg',thumb)[1].tobytes()
            #value = base64.b64encode(cv2.imencode('.jpeg',thumb)[1].tobytes())
            self.generated_data['image'] = value.decode("utf-8")
        else:
            return
           
    def save_data(self):
        with open(str(self.generated_data['acq_path'] + 'results.pickle'), 'wb') as handle:
                  pickle.dump(self.generated_data,
                              handle,
                              protocol=pickle.HIGHEST_PROTOCOL)
       
    #def update_display(self):
    #    self.display = Display()
    #    dt = str(rtc_now['data']['year']) + '-' + str(rtc_now['data']['month']) + '-' + str(rtc_now['data']['day'])
    #    self.display.update_acquisition_display(self.config['device_id'],
                                               #self.config['thingsboard'],
                                               #self.batt_vlt,
                                               #dt)
        
    def close(self):
        print('closing')
        # Reset the watchdog to "off" or it will reboot the Pi 10 mins after shutdown.         
        #self.pijuice.power.SetWatchdog(0)    
        # Set power off delay (seconds) to ensure power supplied for long enough for safe shutdown
        # Use SetWatchdog to set time in minutes between acquisitions.
        self.pijuice.power.SetWatchdog(self.config["acq_delay"])
        self.pijuice.power.SetPowerOff(30)
        time.sleep(1)
        #  Shut down the RPi
        os.system('sudo halt')
        
    def collect_data(self):
        print('[INFO]: Running Acquisition')
        for f in range(1, len(self.data_acquisition_pipeline)+1):
            print(self.data_acquisition_pipeline[f])
            self.data_acquisition_pipeline[f]()



#dp = Deployment()
#dp.collect_data()

#run()
# Self contained loop..
#while(True):
#    run()
#    time.sleep(240)
