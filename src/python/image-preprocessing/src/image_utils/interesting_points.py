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
from image_utils import dicom_utils


def getLineEquation(point1, point2) :
    (x1, y1) = point1
    (x2, y2) = point2
    m = (y1 - y2) / (x1 - x2)
    b = y1 - (x1 * m)
    return m,b



def getLowestPointsFemur(originalImage, tresholdedImage):
    """
    Finds the lowest points of a femur bone in a CT DICOM image

    @param originalImage: non-procesated image
    @param thresholdedImage: binary image after an threshold operation
    """

    contours, _ = cv2.findContours(tresholdedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key = cv2.contourArea, reverse= True)
    half_one = sorted_contours[0]
    half_two = sorted_contours[1]
    originalImage = originalImage.astype(np.uint8)
    bgrImage = cv2.cvtColor(originalImage, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgrImage, [half_one], 0, (0,255,0), 1)
    cv2.drawContours(bgrImage, [half_two], 0, (255,0,0), 1)
    p1 = tuple(half_one[half_one[:, :, 1].argmax()][0])
    p2 = tuple(half_two[half_two[:, :, 1].argmax()][0])
    m,b =getLineEquation(p1,p2)
    point1 = (int) (m * 0 + b)
    point2 = (int) (m * bgrImage.shape[1] + b)
    print(point2)
    cv2.circle(bgrImage, p1, 1, (0, 50, 255), -1)
    cv2.circle(bgrImage, p2, 1, (0, 50, 255), -1)
    cv2.line(bgrImage, (0, point1), (bgrImage.shape[1], point2), (255,80,0), 1)

    return bgrImage, m

def getTransvesalPointRotula(originalImage, thresholdedImage, femurSlope):
    """
    Finds the transvesal points of a rotula bone in a CT DICOM image

    @param originalImage: non-procesated image
    @param thresholdedImage: binary image after an threshold operation
    @param femurSlope: slope part of the line of the lowest points of the femur
    """
    
    contours, _ = cv2.findContours(thresholdedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key = cv2.contourArea, reverse= True)
    rotula_contour = sorted_contours[1]
    originalImage = originalImage.astype(np.uint8)
  #  originalImage = cv2.cvtColor(originalImage, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(originalImage, [rotula_contour], 0, (255,0,0), 1)
    top = tuple(rotula_contour[rotula_contour[:, :, 1].argmin()][0]) 
    bottom = tuple(rotula_contour[rotula_contour[:, :, 1].argmax()][0])
    cv2.circle(originalImage, top, 1, (0, 50, 255), -1)
    cv2.circle(originalImage, bottom, 1, (0, 50, 255), -1)
    m, b = getLineEquation(top, bottom)
    slope = -1 / m 
    midpointX = (top[0] + bottom[0]) / 2 
    midpointY = (top[1] + bottom[1]) / 2
    b2 = -slope * midpointX + midpointY
    point1 = (int) (slope * 0 + b2)
    point2 = (int) (slope * originalImage.shape[1] + b2)
    cv2.line(originalImage, (0, point1), (originalImage.shape[1], point2), (255,80,0), 1)
    point3 =  (int) (femurSlope * 0 + b2)
    point4 = (int) (femurSlope * originalImage.shape[1] + b2)
    cv2.line(originalImage, (0, point3), (originalImage.shape[1], point4), (255,80,0), 1)

    return originalImage


def getPointsFemur(img, angle):
    """
    Finds the lowest points of a femur bone in a CT DICOM image

    @param originalImage: non-procesated image
    @param angle: angle of the femur bone
    """

    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    c = max(contour_sizes, key=lambda x: x[0])[1]
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    extTop = tuple(c[c[:, :, 1].argmin()][0])
    extBot = tuple(c[c[:, :, 1].argmax()][0])
    center = (int)  ((extLeft[0] + extRight[0]) / 2)
    img[:, center] = 0
    for i in  range(img.shape[0]-1):
        for j in range(img.shape[1]-1):
            if extTop[1] > i :
                img[i][j] = 0   #remove rotula
    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.cvtColor(img.astype('float32'), cv2.COLOR_GRAY2BGR)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    c = max(contour_sizes, key=lambda x: x[0])[1]
    sorted_contours = sorted(contours, key = cv2.contourArea, reverse= True)
    left_femur = sorted_contours[1]
    extBot = tuple(c[c[:, :, 1].argmax()][0])
    leftBot = tuple(left_femur[left_femur[:,:,1].argmax()][0])
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h),
    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE) 
    transform_points = np.array( [ [ [ extBot[0], extBot[1] ] ],  [ [ leftBot[0], leftBot[1] ] ]  ])
    tf2 = cv2.transform(transform_points, M)
    cv2.circle(rotated, (tf2[0][0][0], tf2[0][0][1]), radius=0, color=(0, 0, 255), thickness=-1)
    cv2.circle(rotated, ( tf2[1][0][0], tf2[1][0][1]), radius=0, color=(0, 0, 255), thickness=-1)
    return rotated, (tf2[0][0], tf2[1][0])
