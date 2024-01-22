import numpy as np
import imageio


def open_image_to_bw_array(filename, threshold=255):
    image = imageio.v2.imread(filename, mode='L')
    return np.minimum(image, threshold)
