import matplotlib.pyplot as plt
import numpy as np
import cv2
from tqdm import tqdm
import os
from collections import Counter

from jpeg_decoder import *

cover_dir = 'covers_jpeg/'
stego_dir = 'stegos_jpeg/'
histograms = 'histograms_jpeg'
'''
cover_dir = 'covers_png/'
stego_dir = 'stegos_lsb/'
histograms = 'histograms_lsb'
'''

for img in tqdm(os.listdir(cover_dir)):
    cover_path = os.path.join(cover_dir, img)
    stego_path = os.path.join(stego_dir, 'stego_' + img)

    cover = cv2.imread(cover_path, 0)
    stego = cv2.imread(stego_path, 0)

    cover = cover.flatten()
    stego = stego.flatten()

    difference = []

    for i in range(len(cover)):
        difference.append(int(cover[i]) - int(stego[i]))

    difference = np.array(difference)

    hist, bins = np.histogram(difference, bins=100)
    width = (bins[1] - bins[0])

    center = (bins[:-1] + bins[1:])/2

    plt.bar(center, hist, align='center', width=width)
    plt.title(img)
    plt.savefig(histograms + '/difference_hist_' + os.path.splitext(img)[0] + '.png')
