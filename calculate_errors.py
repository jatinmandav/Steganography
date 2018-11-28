import numpy as np
import os
from tqdm import tqdm
import cv2

def calculate_mse(cover, stego):
    mse_val = 0
    (h, w) = cover.shape[:2]
    for i in range(h):
        for j in range(w):
            mse_val += (int(cover[i][j]) - int(stego[i][j]))**2

    return mse_val/(w*h)
'''
cover_dir = 'covers_jpeg/'
stego_dir = 'stegos_jpeg/'
mse_psnr_file = 'mse_psnr_jpeg.csv'
'''

cover_dir = 'covers_png/'
stego_dir = 'stegos_lsb/'
mse_psnr_file = 'mse_psnr_lsb.csv'

with open(mse_psnr_file, 'w') as f:
    content = 'cover_path,stego_path,mse,psnr\n'
    f.write(content)

mse = 0
psnr = 0
R = 255

num_images = len(os.listdir(stego_dir))

for img in tqdm(os.listdir(cover_dir)):
    cover_path = os.path.join(cover_dir, img)
    stego_path = os.path.join(stego_dir, 'stego_' + img)

    cover = cv2.imread(cover_path, 0)
    stego = cv2.imread(stego_path, 0)

    # Calculate MSE
    mse_val = calculate_mse(cover, stego)
    mse += mse_val

    psnr_val = 10*np.log(R**2/mse_val)
    psnr += psnr_val

    with open(mse_psnr_file, 'a') as f:
        content = str(cover_path) + ',' + str(stego_path) + ',' +\
                    str('{:.04f}'.format(mse_val)) + ',' + str('{:.04f}'.format(psnr_val)) + '\n'
        f.write(content)


avg_mse = float(mse)/num_images
avg_psnr = float(psnr)/num_images

with open(mse_psnr_file, 'a') as f:
    content = str('-') + ',' + str('-') + ',' +\
                str('Average_MSE:{:.04f}'.format(avg_mse)) + ',' + str('Average_PSNR:{:.04f}'.format(avg_psnr)) + '\n'
    f.write(content)


print(avg_mse, avg_psnr)
