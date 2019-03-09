from glob import glob
from scipy.misc import imread, imsave, imresize
import os
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--valsize', type=int, default=100)
parser.add_argument('--imsize', type=int, default=128)
args = parser.parse_args()

def gen_concat_dataset(names, is_train, im_size, cropped_dir, dataset_dir):
    if is_train:
        mode = "train"
    else:
        mode = "val"

    for name in names:
        im_path = os.path.join(cropped_dir, name)
        im = imread(im_path)
        im = np.rot90(im)
        im = imresize(im, (im_size, im_size*2))
        imsave(os.path.join(dataset_dir, mode, name), im)
        print(name)

val_size = args.valsize
im_size = args.imsize
cropped_dir = "input/cropped"
dataset_dir = "datasets/face{}".format(im_size)
train_dir = os.path.join(dataset_dir, "train")
val_dir = os.path.join(dataset_dir, "val")
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

names = np.array(os.listdir(cropped_dir))
np.random.seed(1)
names = np.random.permutation(names)
train_names = names[val_size:]
val_names = names[:val_size]

gen_concat_dataset(train_names, True, im_size, cropped_dir, dataset_dir)
gen_concat_dataset(val_names, False, im_size, cropped_dir, dataset_dir)