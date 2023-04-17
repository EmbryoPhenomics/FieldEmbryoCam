#  Python script to test GPIO signalling to switch between states:
#  streaming (for setup) and deployment (for acqusitions)

import RPi.GPIO as GPIO
import time
import threading
from collections import deque 
from _run_deployment import Deployment
from _run_live import Stream

class FieldEmbryoCam:

    def setup(self):
        #  Set pin reference to physical pin number for ease of use.
        GPIO.setmode(GPIO.BOARD)
        #  Alternatively use BCM channel numbers: GPIO.setmode(GPIO.BCM)
        #  Setup desired channel, and define as an output.
        self.switch_pin = 37
        GPIO.setup(self.switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def launch(self):
        self.setup()
        mode = GPIO.input(int(self.switch_pin))

        if mode == 0:
            print ("[INFO]: Deployment mode activated")
            # self.switch_queue.popleft(0) 
            deployment = Deployment()
            deployment.collect_data()  
        else:
            print ("[INFO]: Streaming mode activated")
            # self.switch_queue.popleft(0)
            st = Stream()
            st.cam_stream()

#while True:
fieldec = FieldEmbryoCam()
fieldec.launch()
