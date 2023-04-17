# Image handling
#from skimage.util import view_as_blocks
import numpy as np 
import vuba
import cv2
import math

# Power spectral analysis
from scipy import signal

# Plotting 
# import matplotlib.pyplot as plt


class Analysis():
	def __init__(self, path, blocksize = 8, species = 'unspecified'):
		# Retrieve footage and read in frames
		video = vuba.Video(path + '*.jpg')
		frames = video.read(0, len(video), grayscale=True)

		# Grid size for EPT calculation 
		self.blocksize = blocksize
		self.species = species

	# Computation of EPTs -------------------------------------------------------------
	def crop(frame):
		'''Crop an image according to the blocksize required for EPT calculation.'''
		# Floor used so new image size is always below the original resolution
		new_x, new_y = map(lambda v: math.floor(v/blocksize)*blocksize, frame.shape) 
		return frame[:new_x, :new_y]


	def calculate_epts(self):
		# Compute mean pixel values 
		x,y = video.resolution
		block_shape = tuple(map(int, (x/blocksize, y/blocksize)))
		mpx = np.asarray([view_as_blocks(frame, block_shape).mean(axis=(2,3)) for frame in map(crop, frames)])

		# Compute power spectral data
		epts = np.empty((blocksize, blocksize, 2, int(len(video)/2)+1))
		for i in range(blocksize):
			for j in range(blocksize):
				epts[i,j,0,:], epts[i,j,1,:] = signal.welch(mpx[:,i,j], fs=video.fps, scaling='spectrum', nfft=len(mpx))
