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

def thresholdCTImage(img,c,w):
    """
    Thresolds and DICOM CT image, returning a binary image

    :param img: Image to be processed
    :param c: Window Center of the DICOM image
    :param w: Window Width of the DICOM image
    """

    window_center = c
    window_width = w
    normalized_image = dicom_utils.normalizeImage(img, window_center, window_width)
    mag_image = dicom_utils.magnitude(normalized_image)
    bins = 70
    histogram, _ = np.histogram(normalized_image, bins=bins, range=(0, 1))
    gap = mag_image * 2
    hist_value_selected = 0
    for i in histogram:
        if i <= gap:
            break
        hist_value_selected = hist_value_selected + 1
    threshold = 0.5
    mask = dicom_utils.getMask(normalized_image, threshold)
    return mask


def drawCTContours(originalImage, tresholdedImage):
    """
    Finds and draws into original image contours found in a thresholded image

    :param originalImage: Image to be drawed
    :param thresholdedImage: image thresholded
    """

    contours, _ = cv2.findContours(tresholdedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    bgrImage = cv2.cvtColor(originalImage, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgrImage, contours, -1, (0, 255, 0), 1) 
    return bgrImage, contours


def cropFemurCT(originalImage):
    """
    Crops the femur region of the CT image

    :param originalImage: image to be cropped
    """

    h, w = originalImage.shape
    newHeigth = (int) (np.floor(h / 2))
    newWidth = (int)  (np.floor( w / 2))
    croppedImage = originalImage[160:325, 112:250]
    moments = cv2.moments(croppedImage)
    cX = int(moments["m10"] / moments["m00"])
    cY = int(moments["m01"] / moments["m00"])
    croppedImage[:,cX] = 0
    return croppedImage



def cropRotulaCT(originalImage):
    """
    Crops the rotula region of the CT image

    :param originalImage: image to be cropped
    """

    h, w = originalImage.shape
    newHeigth = (int) (np.floor(h / 2))
    newWidth = (int)  (np.floor( w / 2))
    croppedImage = originalImage[160:325, 112:250]
    return croppedImage


def getROI(img):
    """
    Crops the ROI of the CT image

    :param originalImage: image to be cropped
    """

    img2 = img.copy()
    half_column = img.shape[1] / 2
    for i in range(img.shape[0]-1):
        for j in range(img.shape[1]-1):
            if j> half_column:
                img2[i][j] = 0
    return img2


def rotateFemur(img):
    """
    Rotates image in a way which Femur bone is pararel to the margins of the image
    
    :param img: image to be rotated
    """

    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]

    biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
    rect = cv2.minAreaRect(biggest_contour)
    angle = rect[2]

    if angle < -45:
        angle = (90 + angle)

# otherwise, just take the inverse of the angle to make
# it positive
    else:
        angle = -angle  
    print(angle)
# rotate the image to deskew it
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h),
    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE) 
  #  cv2.drawContours(img, [biggest_contour], 0, (0,255,0), 3)
    return rotated, angle



def rotate_rotula(img):
    """
    Rotates image in a way which transvesal points of Rotula bone are pararel to the margins of the image

    :param img: image to be rotated
    """

    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key = cv2.contourArea, reverse= True)
    femur = sorted_contours[0]
    extTop = tuple(femur[femur[:, :, 1].argmin()][0])
    for i in  range(img.shape[0]-1):
        for j in range(img.shape[1]-1):
            if extTop[1] < i :
                img[i][j] = 0   #remove anything
    rotula_contour = sorted_contours[1]
    rect = cv2.minAreaRect(rotula_contour)
    angle = rect[2]

    if angle < -45:
        angle = (90 + angle)

# otherwise, just take the inverse of the angle to make
# it positive
    else:
        angle = -angle  
    print(angle)
# rotate the image to deskew it
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h),
    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE) 
    contours, _ = cv2.findContours(rotated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key = cv2.contourArea, reverse= True)
    c = sorted_contours[0]
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    transform_points = np.array( [ [ [ extLeft[0], extLeft[1] ] ],  [ [ extRight[0], extRight[1] ] ]  ])
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h),
    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE) 
    tf2 = cv2.transform(transform_points, M)

    return rotated, (tf2[0][0], tf2[1][0])

