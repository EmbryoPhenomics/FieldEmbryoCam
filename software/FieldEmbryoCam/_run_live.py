# Web streaming example from here:
# https://randomnerdtutorials.com/video-streaming-with-raspberry-pi-camera/
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

#  To receive the stream enter the Pi's IP address, suffixed with :8000 on a web browser
from display import Display
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import threading
import RPi.GPIO as GPIO
import time
import os
from pijuice import PiJuice
import json

PAGE="""\
<html>
<head>
<title>FieldEP stream</title>
</head>
<body>
<center><h1>FieldEP setup stream</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
<center><p>Check that the camera is in focus when submerged.</p></center.
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
        
    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)
            
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with self.output.condition:
                        self.output.condition.wait()
                        frame = self.output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class MonitorSwitch():
    def __init__(self,mode_pin=37):
        self.mode_pin = mode_pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.mode_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #self.switch_queue = deque(maxlen=1)
        
    def _function_switch(self):
        self.pijuice = PiJuice(1, 0x14)
        self.kill_switch = False
        old_switch_status = GPIO.input(int(self.mode_pin))
        time.sleep(1)
        new_switch_status = GPIO.input(self.mode_pin)
        if new_switch_status is not old_switch_status:
            self.kill_switch = True
            print ("[INFO]: Switching updated")
            self.pijuice.power.SetPowerOff(30)
            time.sleep(1)
            os.system('sudo halt')
            #self.switch_queue.append(new_switch_status)
            #new_switch_status = new_switch_status
            #old_switch_status = new_switch_status
            #print(old_switch_status)
            
    def function_switch(self):
        while True:
            self._function_switch()
          
    def run(self):
        #self.setup()
        self.switch_thread = threading.Thread(target=self.function_switch)
        self.switch_thread.start()

class Stream():
    def __init__(self, LED_pin=15):
        self.LED_pin = LED_pin
        
        # Load config and initiate display
        with open('./config.json', 'r') as cfg:
            self.config = json.load(cfg)
        
        # Get batt info.
        pj = PiJuice(1, 0x14)
        chrg = pj.status.GetChargeLevel()
        vlt = pj.status.GetBatteryVoltage()
        
        # Get date and time.
        rtc_now = self.pijuice.rtcAlarm.GetTime()
        dt = '[INFO]: Date: ' + str(rtc_now['data']['year']) + '-' + str(rtc_now['data']['month']) + '-' + str(rtc_now['data']['day'])
        self.display = Display()
        self.display.update_stream_display(self.config['device_id'],
                                  self.config['thingsboard'],
                                  vlt,
                                  dt)
        
    def cam_stream(self):
        # Initialise LED pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.LED_pin, GPIO.OUT)
        GPIO.output(self.LED_pin, GPIO.HIGH)
        # Instantiate PiJuice interface object
        self.pijuice = PiJuice(1, 0x14)
        self.pijuice.power.SetWatchdog(0)
        
        
        with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
            address = ('', 8000)
            output = StreamingOutput()

            #Uncomment the next line to change your Pi's Camera rotation (in degrees)
            #camera.rotation = 90
            camera.start_recording(output, format='mjpeg')
            StreamingHandler.output = output
            server = StreamingServer(address, StreamingHandler)
            
            kill = MonitorSwitch()
            kill.run()
            
            while not kill.kill_switch:
                server.handle_request()
            else:
                # Closing stream
                print('[INFO]: Closing stream')
                GPIO.output(self.LED_pin, GPIO.LOW)
                camera.stop_recording()
                server.server_close()
