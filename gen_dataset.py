from glob import glob
from scipy.misc import imread, imsave, imresize
import os
import numpy as np

def gen_concat_dataset(names, is_train, im_size, dataset_dir):
    if is_train:
        mode = "train"
    else:
        mode = "val"

    for name in names:
        top_path = os.path.join(top_dir, name)
        bottom_path = os.path.join(bottoms_dir, name)
        top_im = imread(top_path)
        top_im = imresize(top_im, (im_size, im_size))
        top_im = np.rot90(top_im)
        bottom_im = imread(bottom_path)
        bottom_im = imresize(bottom_im, (im_size,im_size))
        bottom_im = np.rot90(bottom_im)
        concat_im = np.concatenate((top_im, bottom_im), axis=1)
        imsave(os.path.join(dataset_dir, mode, name), concat_im)
        print(name)

val_size = 2000
im_size = 256
top_dir = "input/image_top/"
bottoms_dir = "input/image_bottom/"
dataset_dir = "datasets/face{}".format(im_size)
train_dir = os.path.join(dataset_dir, "train")
val_dir = os.path.join(dataset_dir, "val")
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

names = np.array(os.listdir(top_dir))
np.random.seed(1)
names = np.random.permutation(names)
train_names = names[val_size:]
val_names = names[:val_size]



gen_concat_dataset(train_names, True, im_size, dataset_dir)
gen_concat_dataset(val_names, False, im_size, dataset_dir)