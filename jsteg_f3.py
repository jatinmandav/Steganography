import sys
import os
import argparse
from PIL import Image
import io

from jpeg_encoder import *
from jpeg_decoder import *

import math
import random
from B import *

from tqdm import tqdm

def create(value=None, *args):
    if len(args) and args[0]:
        return [create(value,*args[1:]) for i in range(round(args[0]))]
    else: return value

class Encoder:
    def __init__(self, image, quality, out):
        self.out = out
        self.jpeg_encoder = jpegEncoder(image, quality, out, 'by: Jatin Mandav')

    def write(self, data, password):
        self.data = data
        self.password = password
        self.jpeg_encoder.writeHeads()

        self.embedData_f3()
        self.jpeg_encoder.writeImage()

    def embedData_f3(self):
        coeff=self.jpeg_encoder.coeff
        byte_embed=len(self.data)
        if byte_embed>0x7fffffff: byte_embed=0x7fffffff
        bit_embed=byte_embed&1
        byte_embed>>=1
        need_embed=31
        data_index=0
        for i,j in enumerate(coeff):
            if i%64==0 or j==0: continue
            if j>0 and (j&1)!=bit_embed: coeff[i]-=1
            elif j<0 and (j&1)!=bit_embed: coeff[i]+=1
            if coeff[i]!=0:
                if need_embed==0:
                    if data_index>=len(self.data): break
                    byte_embed=ord(self.data[data_index])
                    data_index+=1
                    need_embed=8
                bit_embed=byte_embed&1
                byte_embed>>=1
                need_embed-=1
class Decoder:
    def __init__(self, data, out):
        self.out = out
        self.data = data
        self.jpeg_decoder = jpegDecoder(data)

    def read(self, password):
        self.password = password
        self.jpeg_decoder.readHeads()
        self.jpeg_decoder.readImage()

        self.extractData_f3()

    def extractData_f3(self):
        coeff=self.jpeg_decoder.coeff
        i,pos=0,-1
        finish,length=0,0
        need_extract=0
        byte_extract=0
        while i<32:
            pos+=1
            j=pos-pos%64+ZAGZIG[pos%64]
            if j%64==0 or coeff[j]==0: continue
            if coeff[j]&1: length|=1<<i
            i+=1

        while finish<length:
            pos+=1
            j=pos-pos%64+ZAGZIG[pos%64]
            if j%64==0 or coeff[j]==0: continue
            if coeff[j]&1: byte_extract|=1<<need_extract
            need_extract+=1
            if need_extract==8:
                self.out.write(chr(byte_extract&0xff))
                need_extract=0
                byte_extract=0
                finish+=1

'''
cover_dir = 'covers_jpeg/'
stego_dir = 'stegos_jpeg/'
message_file = 'message.txt'
empty_file = 'empty_file.txt'
quality = 90
password = '1111111111'

for img in tqdm(os.listdir(cover_dir)):
    path = os.path.join(cover_dir, img)
    stego_path = os.path.join(stego_dir, 'stego_' + img)
    image = Image.open(path)
    file_ = open(message_file, 'r')
    data = ''.join(file_)

    output = open(stego_path, 'wb')
    encoder = Encoder(image, quality, output)
    encoder.write(data, password)
    output.close()

'''
parser = argparse.ArgumentParser()
parser.add_argument('METHOD', help='"ENCODE" or "DECODE"')
parser.add_argument('-i', '--image', help='Input Image')
parser.add_argument('-f', '--datafile', help='Input Data File to Encode')
parser.add_argument('-o', '--output', help='Path to Output File')
parser.add_argument('-p', '--password', help='Input Password', default='123456')
parser.add_argument('-q', '--quality', default=80, help='Quality of JPG image')

args = parser.parse_args()

if args.METHOD.lower() == 'encode' or args.METHOD.lower() == 'e':
    if not os.path.exists(args.image):
        print('Image not Found!')
        sys.exit(1)
    else:
        image = Image.open(args.image)

    if not os.path.exists(args.datafile):
        print('Data File not Found!')
        sys.exit(1)
    else:
        file_ = open(args.datafile, 'r')
        data = ''.join(file_)

    if not args.output:
        args.output = 'stego.jpg'

    output = open(args.output, 'wb')
    encoder = Encoder(image, args.quality, output)
    encoder.write(data, args.password)
    output.close()
elif args.METHOD.lower() == 'decode' or args.METHOD.lower() == 'd':
    if args.output:
        output = open(args.output, 'w')
    else:
        output = io.StringIO()

        if not os.path.exists(args.image):
            print('Image not Found!')
            sys.exit(1)
        else:
            image = open(args.image, 'rb')
            decoder = Decoder(image.read(), output)
            decoder.read(args.password)

            if not args.output:
                print(output.getvalue())

            image.close()
            output.close()
