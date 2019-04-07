from glob import glob
from scipy.misc import imread, imsave, imresize
import os
import numpy as np
import argparse
from glob import glob

DATASET_DIR = "input/celeba/images"


def process_and_save_images(paths, is_train, im_size, dataset_dir):
    from facecrop import crop_face

    if is_train:
        dir = os.path.join(dataset_dir, "train")
        os.makedirs(dir, exist_ok=True)
    else:
        dir = os.path.join(dataset_dir, "val")
        os.makedirs(dir, exist_ok=True)

    for path in paths:
        im = imread(path)
        im_crop = crop_face(im, (im_size, im_size))
        if not np.isnan(im_crop).any():
            name = os.path.basename(path)
            imsave(os.path.join(dir, name), im_crop)
            print("Processed", name)
        else:
            print("Failed   ", name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--valsize', type=int, default=100)
    parser.add_argument('--imsize', type=int, default=128)
    args = parser.parse_args()

    val_size = args.valsize
    im_size = args.imsize

    dataset_dir = "processed/cropped_{}".format(im_size)
    os.makedirs(dataset_dir, exist_ok=True)

    paths = np.array(glob(os.path.join(DATASET_DIR, "*")))
    np.random.seed(1)
    names = np.random.permutation(paths)
    train_paths = names[val_size:]
    val_paths = names[:val_size]

    process_and_save_images(train_paths, True, im_size, dataset_dir)
    process_and_save_images(val_paths, False, im_size, dataset_dir)