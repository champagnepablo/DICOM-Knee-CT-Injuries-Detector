import math
import random as rng
import cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt
import pydicom
import imutils
from pydicom.data import get_testdata_files
from pydicom.pixel_data_handlers.util import apply_modality_lut
from pydicom.pixel_data_handlers.util import apply_voi_lut


def transformToHu(medical_image, image):
    """
    Returns an medical image into a Housenfield Scale

    :param medical_image: the dicom image 
    :param image: matrix with image to be processed
    """

    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    hu_image = image * slope + intercept
    return hu_image


def normalizeImage(img, window_center, window_width):
    """
    Returns an image into a normalized space [0-1]

    :param img: original image to be processed
    :param window_center: Window center of the DICOM file
    param window_width: Window width of the DICOM file
    """

    normalized_image = np.zeros((img.shape[0],img.shape[1]), dtype = float)
    op1 = window_center - 0.5 - (window_width-1)/2
    op2 = window_center - 0.5 + (window_width-1)/2
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i,j] <= op1 :
                normalized_image[i,j] = 0
            elif img[i,j] > op2 :
                normalized_image[i,j] = 255
            else :
                normalized_image[i,j] = (int) (((img[i,j]-window_center-0.5)/(window_width-1) +0.5) * 255)
    return normalized_image


def getMask(img, threshold):
    """
    Gets mask for an image

    :param img: Image to be processed
    :param threshold: Threshold value
    """

    mask = np.zeros((img.shape[0],img.shape[1]), dtype = np.uint8)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i,j] >= threshold:
                mask[i,j] = 1
    return mask


def magnitude(img):
    """
    Calculates magnitude of an image

    :param img: Image of which be calculated the magnitude
    """
    
    magnitude = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            magnitude = magnitude + pow(img[i,j],2)
    magnitude = math.sqrt(magnitude)
    return magnitude
