import tensorflow as tf
from model import pix2pix
import argparse
from scipy.misc import imread, imsave
from facecrop import crop_face
from utils import resize_and_rotate

def gen_mouth_img(img, dataset_name, fine_size):
    model = pix2pix(tf.Session(), dataset_name=dataset_name, image_size=128, batch_size=1, output_size=fine_size,
                    checkpoint_dir="checkpoint/")
    im_s = model.test_1_image(img)
    return im_s

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('path', help="image file path")
    parser.add_argument('--dataset_name', default='face128', help='name of the dataset')
    parser.add_argument('--fine_size', type=int, default=128, help='then crop to this size')
    args = parser.parse_args()

    img = imread(args.path)
    face_img = crop_face(img, (args.fine_size, args.fine_size))
    resized_img = resize_and_rotate(face_img, args.fine_size)
    gen_img = gen_mouth_img(resized_img, args.dataset_name, args.fine_size)

    imsave("test.png", gen_img)
