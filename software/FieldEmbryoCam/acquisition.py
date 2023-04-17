from picamera.array import PiRGBArray
import picamera.array
from picamera import PiCamera
from picamera.streams import PiCameraCircularIO
import cv2
import time
from fractions import Fraction
import io

class Acquisition():
	def __init__(self):
		self.acquiring = True
	
	def initialise_cam(self, resolution = (1024,768), framerate = 30):
		self.camera = PiCamera()
		self.resolution = resolution
		self.framerate = framerate
		
		self.camera.resolution = resolution
		self.camera.shutter_speed=50000
		self.camera.framerate=30
		self.camera.exposure_mode = 'off'
		self.camera.awb_mode = 'off'
		
		time.sleep(2)

	def acquire_image(self, path):
		'''
		Does not work!!
		'''
		print('acquiring')
		time.sleep(1)
		self.camera.capture(path, resize=(100,100))
		time.sleep(0.3)

	def acquire_seq(self, frames, path):
		fpath = str(path +'img_%03d.jpg')
		self.camera.capture_sequence([fpath % i for i in range(frames)],
                                     use_video_port = True)
  
	def acquire_continuous():
		'''
		Does not work
		'''
		rawCapture = PiRGBArray(self.camera, size=(1024,768))
		i = 0
		frames = 100
		for frame in self.camera.continuous(rawCapture, format = 'bgr', use_video_port=True):
			image = frame.array
			rawCapture.truncate(0)
			cv2.imwrite(image, '/home/pi/Desktop/imseq/' + str(i) + '.jpg')
			i = i+1
			if i-1 == frames:
				break
            
	def acquire_vid(self):
		with PiCameraCircularIO(self.camera, seconds=3) as stream:
			self.camera.start_recording(stream, format='h264', splitter_port=2)
			self.camera.wait_recording(10)
			stream.copy_to('/home/pi/Desktop/circ.h264')
			self.camera.stop_recording()
			
	def close(self):
		self.camera.close()
