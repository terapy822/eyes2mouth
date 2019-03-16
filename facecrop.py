import cv2
import numpy as np

def crop_face(img, size=(128, 128)):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    face_classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
    try:
        x, y, w, h = face_classifier.detectMultiScale(img, 1.3, 5)[0]
    except:
        return np.nan
    else:
        image_face = img[y: y + h, x: x + w]
        image_face = cv2.resize(image_face, size)
        image_face = cv2.cvtColor(image_face, cv2.COLOR_BGR2RGB)
        return image_face


if __name__ == '__main__':
    import argparse
    from scipy.misc import imread, imsave
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('path', help="image file path")
    parser.add_argument('--fine_size', type=int, default=128, help='then crop to this size')
    args = parser.parse_args()

    img = imread(args.path)
    crop = crop_face(img, (args.fine_size, args.fine_size))
    imsave("test.png", crop)
