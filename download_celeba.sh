#!/bin/bash

# CelebA images and attribute labels
URL=https://www.dropbox.com/s/d1kjpkqklf0uw77/celeba.zip?dl=0
ZIP_FILE=./input/celeba.zip
mkdir -p ./input/
wget -N $URL -O $ZIP_FILE
unzip $ZIP_FILE -d ./input/
rm $ZIP_FILE