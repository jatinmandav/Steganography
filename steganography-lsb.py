import cv2
import argparse
import sys
import numpy as np
from tqdm import tqdm
import time

parser = argparse.ArgumentParser()
parser.add_argument('METHOD', help="Encode or Decode", type=str)
parser.add_argument("IMAGE", help="Path to Image in which the Message is to be encoded.", type=str)

parser.add_argument("--file", help="Path to file containing the secret message.", type=str)
parser.add_argument("--output_file", help="Path to file to WRITE decoded message", type=str)
parser.add_argument("--message", help="Message to Encode in Given image | Default='This message is encoded using Steganography'", type=str, default="This message is encoded using Steganography")
parser.add_argument('--output', help="Output File Name or Path | Default='output_image.png'", type=str, default="output_image.png")

args = parser.parse_args()
method = args.METHOD
cover_image = args.IMAGE
output_file = args.output_file

stego_image = args.output

if args.file:
    with open(args.file, 'r', buffering=2000) as fp:
        message = fp.read()
else:
    message = args.message

message += "~"

def generate_binary_from_text(message):
    binary_message = []
    for character in message:
        order = ord(character)
        binary_message += [int(bit) for bit in list('{0:08b}'.format(order))]

    return binary_message

def encode_stego_image(cover_image, message, stego_image):
    start_time = time.time()
    cover_image = cv2.imread(cover_image)
    message_binary = generate_binary_from_text(message)
    i = 0

    img_size = cover_image.shape[0]*cover_image.shape[1]

    if len(message_binary) >= img_size:
        print("Message Exceeds the Image Limit. :(")
        sys.exit(1)

    new_img = np.zeros(cover_image.shape)
    j = 0
    leng = len(message_binary)

    with tqdm(total=(cover_image.shape[0]*cover_image.shape[1])) as progress_bar:
        progress_bar.set_description("Encoding Message")
        for h in range(len(cover_image)):
            for w in range(len(cover_image[0])):
                if i < len(message_binary):
                    modified_pixel = (cover_image[h][w][0] & ~1) | message_binary[i]
                    new_img[h][w][0] = modified_pixel
                else:
                    new_img[h][w][0] = cover_image[h][w][0]

                new_img[h][w][1] = cover_image[h][w][1]
                new_img[h][w][2] = cover_image[h][w][2]

                i += 1
                progress_bar.update(1)

    cv2.imwrite(stego_image, new_img)
    print("Message Encoded to {} in {:03f} Seconds.".format(stego_image, time.time() - start_time))
    return

def decode_stego_image(stego_image):
    start_time = time.time()

    message_binary = ''
    characters = []
    i = 0
    stego_image = cv2.imread(stego_image)

    for h in range(len(stego_image)):
        for w in range(len(stego_image[0])):
            message_binary += str(stego_image[h][w][0] & 0x01)
            i += 1
            if i == 8:
                char = chr(int(message_binary, 2))
                if char == "~":
                    if output_file:
                        with open(output_file, 'w') as f:
                            f.write("".join(characters))
                    else:
                        print("".join(characters))

                    print("Message Decoded in {:02f} Seconds".format(time.time() - start_time))

                    return
                characters.append(char)
                i = 0
                message_binary = ''

if method.lower() == "encode":
    encode_stego_image(cover_image, message, stego_image)
elif method.lower() == 'decode':
    decode_stego_image(stego_image)
else:
    print("Invalid Choice: METHOD: encode or decode")
    sys.exit()
