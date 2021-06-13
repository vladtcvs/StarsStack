import matplotlib.pyplot as plt
from skimage import measure
import numpy as np
import sys
import cv2
import usage
import os
import common
import multiprocessing as mp

import stars.detect

ncpu = 11
k = 4

sky_blur = 351

def fun(l):
	return 2/(l**2+1) - 1

def interp(y, x, h, w):
	L = ((w/2)**2+(h/2)**2)**0.5
	x -= w/2
	y -= h/2
	l = (x**2+y**2)**0.5
	return fun(l/L)

def skymodel_gauss(image, stars_mask):
	shape = image.shape
	sky = np.zeros(shape)
	idx  = (stars_mask==0)
	nidx = (stars_mask!=0)
	sky[idx]  = image[idx]
	average   = np.mean(sky, axis=(0,1))
	sky[nidx] = average
	sky = cv2.GaussianBlur(sky, (sky_blur, sky_blur), 0)
	return sky


def remove_sky(name, infname, outfname, method):
	print(name)
	image = np.load(infname)["arr_0"]
	shape = image.shape

	visible = image
	nch = shape[2]-1
	print("Image has %i channels" % nch)

	visible = image[:,:,0:nch]

	mask = stars.detect.detect(visible)[1]
	if method == "gauss":
		sky = skymodel_gauss(visible, mask)
	else:
		sky = skymodel_gauss(visible, mask)


	result = visible - sky

#	fig = plt.figure()

#	fig.add_subplot(2, 2, 1)
#	plt.imshow(visible  / np.amax(visible))

#	fig.add_subplot(2, 2, 2)
#	plt.imshow(mask)

#	fig.add_subplot(2, 2, 3)
#	plt.imshow(sky  / np.amax(visible))

#	fig.add_subplot(2, 2, 4)
#	plt.imshow(result  / np.amax(visible))

#	plt.show()


	image[:,:,0:nch] = result

	np.savez_compressed(outfname, image)

def process_file(argv):
	infname = argv[0]
	outfname = argv[1]
	if len(argv) == 2:
		method = "gauss"
	else:
		method = argv[2]
	name = os.path.splitext(os.path.basename(infname))[0]
	remove_sky(name, infname, outfname, method)

def process_dir(argv):
	inpath = argv[0]
	outpath = argv[1]
	if len(argv) == 2:
		method = "gauss"
	else:
		method = argv[2]
	files = common.listfiles(inpath, ".npz")
	pool = mp.Pool(ncpu)
	pool.starmap(remove_sky, [(name, fname, os.path.join(outpath, name + ".npz"), method) for name, fname in files])
	pool.close()

def process(argv):
	if os.path.isdir(argv[0]):
		process_dir(argv)
	else:
		process_file(argv)

commands = {
	"*" : (process, "Remove sky from image", "(input.file output.file | input/ output/) [method]"),
}

def run(argv):
	usage.run(argv, "image-fix remove-sky", commands, "Methods: gauss")
