import matplotlib.pyplot as plt
from skimage import measure
import numpy as np
import sys
import cv2
import usage
import os
import common
import multiprocessing as mp

import cfg
import sky_model.isoline_model
import stars.detect

ncpu = 11
k = 4
build_model = False
sky_blur = 111

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


def remove_sky(name, infname, outfname):
	print(name)

	img = common.data_load(fname)
	for channel in img["meta"]["channels"]:
		if channel in img["meta"]["encoded_channels"]:
			continue
		image = img["channels"][channel]

		mask = stars.detect.detect(image)[1]
		sky = skymodel_gauss(image, mask)

		result = visible - sky
		
		common.data_add_channel(img, result, channel)
		
	common.data_store(img, outfname)
	
def process_file(argv):
	infname = argv[0]
	outfname = argv[1]
	name = os.path.splitext(os.path.basename(infname))[0]
	remove_sky(name, infname, outfname)

def process_dir(argv):
	inpath = argv[0]
	outpath = argv[1]
	files = common.listfiles(inpath, ".zip")
	pool = mp.Pool(ncpu)
	pool.starmap(remove_sky, [(name, fname, os.path.join(outpath, name + ".zip")) for name, fname in files])
	pool.close()

def process(argv):
	if len(argv) > 0:
		if os.path.isdir(argv[0]):
			process_dir(argv)
		else:
			process_file(argv)
	else:
		process_dir([cfg.config["paths"]["npy-fixed"], cfg.config["paths"]["npy-fixed"]])

commands = {
	"*" : (process, "Remove sky from image", "(input.file output.file | input/ output/)"),
}

def run(argv):
	usage.run(argv, "image-fix remove-sky gauss", commands, "")
