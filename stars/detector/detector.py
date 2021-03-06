import sys

from imutils import contours
from skimage import measure
import numpy as np
import matplotlib.pyplot as plt
import cv2
import imutils
import math
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters

from scipy.ndimage.morphology import generate_binary_structure, binary_erosion
from scipy.ndimage.filters import maximum_filter

import skimage.segmentation as seg
import skimage.filters as filters
import skimage.draw as draw
import skimage.color as color
import skimage.measure as measure

import cfg

def check_round(image, x, y, r):
	x = int(x+0.5)
	y = int(y+0.5)
	r = int(r+0.5)
	block = image[y-r:y+r+1, x-r:x+r+1]
	pos_mask = np.zeros(block.shape)
	cv2.circle(pos_mask, (r, r), r, 1, -1)
	num_circle = cv2.countNonZero(pos_mask)
	num_real = cv2.countNonZero(pos_mask*block)
	if num_real < num_circle*0.55:
		return False
#	print(num_real, num_circle)
#	plt.imshow(block)
#	plt.show()
	return True

def find_stars(starsimage, original=None, debug=False):
	
	min_pixels = 3

	shape = starsimage.shape
	labels = measure.label(starsimage, connectivity=2, background=0)
	mask = np.zeros(shape, dtype="uint8")

	for label in np.unique(labels):
		if label == 0:
			continue

		labelMask = np.zeros(shape, dtype="uint8")
		labelMask[labels == label] = 255
		numPixels = cv2.countNonZero(labelMask)

		# drop too small
		if numPixels < min_pixels:
			continue

		mask = cv2.add(mask, labelMask)

	mask = mask.copy()

#	if debug:
#		plt.imshow(mask, cmap="gray")
#		plt.show()

	cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = contours.sort_contours(cnts)[0]

	stars = []

	if debug:
		image = original / np.amax(original)

	# loop over the contours
	for (i, c) in enumerate(cnts):
		((cX, cY), radius) = cv2.minEnclosingCircle(c)
		if not check_round(mask, cX, cY, radius):
			continue

		stars.append({"x":cX, "y":cY, "size":radius})
		if debug:
			vr = int(radius+0.5)
			cv2.circle(image, (int(cX+0.5), int(cY+0.5)), vr, (1, 0, 0), 1)
	if debug:
		plt.imshow(image/np.amax(image))
		plt.show()

	stars.sort(key=lambda s : -s["size"])
	return stars, mask


def detect_stars(image, debug=False):
	sources = []

	for channel in image["channels"]:
		if channel in image["meta"]["encoded_channels"]:
			continue
		layer = image["channels"][channel]
		layer = layer / np.amax(layer)
		sources.append(layer)

	gray = sum(sources)

	w = gray.shape[1]
	h = gray.shape[0]

	gray = gray / np.amax(gray)
	gray = cv2.GaussianBlur(gray, (3, 3), 0)

	blurred = cv2.GaussianBlur(gray, (31, 31), 0)
	mask = (gray - blurred) > cfg.config["stars"]["brightness_over_neighbours"]

	border = 30
	mask[:,0:border] = 0
	mask[0:border,:] = 0
	mask[:,(w-border):w] = 0
	mask[(h-border):h,:] = 0

#	if debug:
#		plt.imshow(mask, cmap="gray")
#		plt.show()

#	mask = mask.astype(np.uint8)
#	circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, minDist=10, minRadius=1, maxRadius=10)
#	print(circles)

#	orig = image[:,:,0:3]**0.4
	return find_stars(mask)

if __name__ == "__main__":
	filename = sys.argv[1]
	image = np.load(filename)["arr_0"]
	detect_stars(image, True)

