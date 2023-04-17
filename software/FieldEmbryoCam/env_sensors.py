#!/usr/bin/python
import tsys01
import ms5837

from time import sleep
from datetime import datetime
from serial import Serial


class Sensor():
	def __init__(self, sensor_type):
		self.sensor_type = sensor_type

	def initialise(self):
		if self.sensor_type == 'temperature':
			self.sensor = tsys01.TSYS01()
			self.sensor.init()
			if not self.sensor.init():
				print("Error initializing temperature sensor")

		if self.sensor_type == 'pressure':
			self.sensor = ms5837.MS5837()
			self.sensor.init()
			if not self.sensor.init():
				print("Error initializing barometric sensor")
				# exit(1)

	def readSensor(self):
		if self.sensor_type == 'temperature':
			self.sensor.read()
			return self.sensor.temperature()

		if self.sensor_type == 'pressure':
			self.sensor.read()
			return self.sensor.pressure()

