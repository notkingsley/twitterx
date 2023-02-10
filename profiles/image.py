from PIL import Image
import numpy as np


def squash_to_square(file):
	im = Image.open(file)
	sqrWidth = np.ceil(np.sqrt(im.size[0]*im.size[1])).astype(int)
	im_resize = im.resize((sqrWidth, sqrWidth))
	im_resize.save(file)