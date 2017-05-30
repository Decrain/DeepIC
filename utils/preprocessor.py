import cv2
import numpy as np
import random
from sklearn.cluster import k_means
from sklearn.preprocessing import normalize


def imageSIFT(img, n_clusters = 20):
    s = cv2.SURF()
    pic = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    keypoints, descriptors = s.detectAndCompute(pic, None)
    descriptors = normalize(descriptors, norm = 'l2', axis = 1)
    centroid, l, i = k_means(descriptors, n_clusters = n_clusters)
    return np.reshape(centroid, newshape = (1, n_clusters * 64))

# TODO: Rewrite this function to construct a bag-of-word feature
def extractSIFT(images):
    return np.asarray([imageSIFT(images[index]) for index in range(len(images))])


# TODO: SaliencyELD Call - Linrong Jin
# img1 is the original image, img2 is the image processed by SaliencyELD
# the return is the image without background
def removeBackground(img1, img2):
    ret, mask = cv2.threshold(img2, 10, 255, cv2.THRESH_BINARY)
    margin_x, margin_y = np.sum(mask, axis = 0), np.sum(mask, axis = 1)
    left, right, top, bottom = -1, -1, -1, -1
    for i in range(margin_x.shape[0]):
        if margin_x[i] > 0:
            left = i
            break
    for i in range(margin_x.shape[0]):
        if margin_x[margin_x.shape[0] - i - 1] > 0:
            right = margin_x.shape[0] - i - 1
            break
    for i in range(margin_y.shape[0]):
        if margin_y[i] > 0:
            top = i
            break
    for i in range(margin_y.shape[0]):
        if margin_y[margin_y.shape[0] - i - 1] > 0:
            bottom = margin_y.shape[0] - i - 1
            break
    # img1_bg = cv2.bitwise_and(img1, img1, mask = mask)
    return img1[top:bottom, left:right]


def resizeImages(images, size = (64, 64)):
    return np.asarray([cv2.resize(images[index], size) for index in range(images.shape[0])])


def rotateImage(image, angle):
    height = image.shape[0]
    width = image.shape[1]
    height_big = height
    width_big = width
    image_big = cv2.resize(image, (width_big, height_big))
    image_center = (width_big / 2, height_big / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image_big, rot_mat, (width_big, height_big), flags = cv2.INTER_LINEAR)
    return result


# flag = 0 / 1 / -1
def flipImage(image, flag):
    return cv2.flip(image, flag)


def scale(image, multiple, interpolation = None):
    rows, cols, channels = image.shape
    return cv2.resize(image, (int(cols * multiple), int(rows * multiple)), interpolation = interpolation)


def zoom(image, dsize, interpolation = None):
    return cv2.resize(image, dsize, interpolation = interpolation)


def shift(image, x, y):
    M = np.array([[1, 0, x], [0, 1, y]], np.float32)
    rows, cols, channels = image.shape
    return cv2.warpAffine(image, M, (cols, rows))


def contrast(image, alpha, beta):
    image = image * alpha + beta
    return image


def noise(image, size):
    for i in range(0, size):
        xi = int(np.random.uniform(0, image.shape[1]))
        xj = int(np.random.uniform(0, image.shape[0]))
        image[xj, xi] = 255
    return image


def shuffle(image, label, features = None):
    if features is not None:
        _images, _labels, _features = image.tolist(), label.tolist(), features.tolist()
        table = []
        for i in range(len(_images)):
            table.append([_images[i], _labels[i], _features[i]])
        random.shuffle(table)
        return np.asarray([item[0] for item in table]), np.asarray([item[1] for item in table]), np.asarray([item[2] for item in table])
    else:
        _images, _labels = image.tolist(), label.tolist()
        table = []
        for i in range(len(_images)):
            table.append([_images[i], _labels[i]])
        random.shuffle(table)
        return np.asarray([item[0] for item in table]), np.asarray([item[1] for item in table]), None
