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
    if (medical_image == None) :
        raise Exception("Non valid Image passed")
 

    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    hu_image = image * slope + intercept
    return hu_image


def normalizeImage255(img, window_center, window_width):
    """
    Returns an image into a normalized space [0-1]

    :param img: original image to be processed
    :param window_center: Window center of the DICOM file
    param window_width: Window width of the DICOM file
    """

    if (window_center == None):
        raise ValueError("Invalid window_center ")

    if (window_width == None):
        raise ValueError("Invalid window_width ")

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

def normalizeImage(img, window_center, window_width):
    """
    Returns an image into a normalized space [0-1]

    :param img: original image to be processed
    :param window_center: Window center of the DICOM file
    param window_width: Window width of the DICOM file
    """

    if (window_center == None):
        raise ValueError("Invalid window_center ")

    if (window_width == None):
        raise ValueError("Invalid window_width ")

    normalized_image = np.zeros((img.shape[0],img.shape[1]), dtype = float)
    op1 = window_center - 0.5 - (window_width-1)/2
    op2 = window_center - 0.5 + (window_width-1)/2
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i,j] <= op1 :
                normalized_image[i,j] = 0
            elif img[i,j] > op2 :
                normalized_image[i,j] = 1
            else :
                normalized_image[i,j] =  ((img[i,j]-window_center-0.5)/(window_width-1) +0.5) 
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

def mmTranslationPoint(pixel_translation, point):
    x = point[0] * pixel_translation[0]
    y = point[1] * pixel_translation[1]
    return [x,y]

def mmDistanceTwoPoints(pixel_translation, point1, point2):
    """
    Calculates distance in mm given two points (x1,y1) (x2,y2) and a pixel-milimeter translation
    Pre-conditions: pixel_translation must be the same value in both points
    """

    x1 = point1[0] * pixel_translation[0]
    x2 = point2[0] * pixel_translation[0]

    y1 = point1[1] * pixel_translation[1]
    y2 = point2[1] * pixel_translation[1]

    result = math.sqrt( ((x1 - x2) ** 2) + ((y1 - y2) ** 2))

    return result



def getFunctionPoints(point1, point2):
    m = (point2[1] - point1[1]) / (point2[0] - point1[0])
    b = point1[1] - (point1[0] * m)
    return m,b


def getPerpendicularFunction(m, point):
    m_p = - 1 / m
    b = point[1] - (m_p * point[0])
    return m_p, b

def getDistanceParalelLines(m,b1,b2):

    c1 = b1-b2
    c2 = math.sqrt(2*(m **2))
    c = c1 / c2
    return abs(c)