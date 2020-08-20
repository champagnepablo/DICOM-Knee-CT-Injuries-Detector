import math
import random as rng
import cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt
import pydicom
from pydicom.data import get_testdata_files
from pydicom.pixel_data_handlers.util import apply_modality_lut
from pydicom.pixel_data_handlers.util import apply_voi_lut

def getLineEquation(point1, point2) :
    (x1, y1) = point1
    (x2, y2) = point2
    m = (y1 - y2) / (x1 - x2)
    b = y1 - (x1 * m)
    return m,b



def magnitude(img):
    magnitude = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            magnitude = magnitude + pow(img[i,j],2)
    magnitude = math.sqrt(magnitude)
    return magnitude

def getMask(img, threshold):
    mask = np.zeros((img.shape[0],img.shape[1]), dtype = np.uint8)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i,j] >= threshold:
                mask[i,j] = 1
    return mask

def transformToHu(medical_image, image):
    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    hu_image = image * slope + intercept
    return hu_image

def normalizeImage(img, window_center, window_width):
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
                normalized_image[i,j] = (img[i,j]-window_center-0.5)/(window_width-1) +0.5
    return normalized_image
            
def thresholdCTImage(img):
    window_center = 160
    window_width = 2368
    normalized_image = normalizeImage(img, window_center, window_width)
    mag_image = magnitude(normalized_image)
    bins = 70
    histogram, _ = np.histogram(normalized_image, bins=bins, range=(0, 1))
    gap = mag_image * 2
    hist_value_selected = 0
    for i in histogram:
        if i <= gap:
            break
        hist_value_selected = hist_value_selected + 1
    threshold = 0.5
    mask = getMask(normalized_image, threshold)
    return mask


def drawCTContours(originalImage, tresholdedImage):
    contours, _ = cv2.findContours(tresholdedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key = cv2.contourArea, reverse= True)
    bgrImage = cv2.cvtColor(originalImage, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgrImage, contours, -1, (0, 255, 0), 1) 
    return bgrImage, contours

def getLowestPointsFemur(originalImage, tresholdedImage):
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



'''
def getContouredCTImage(originalImage):
    ds = pydicom.dcmread(originalImage)
    hu_scale_image = transformToHu(ds, ds.pixel_array)
    thresholded_ct_image = thresholdCTImage(hu_scale_image)
    contoured_image, contours = getCTContours(hu_scale_image, thresholded_ct_image)
    return contoured_image
'''


def cropFemurCT(originalImage):
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
    h, w = originalImage.shape
    newHeigth = (int) (np.floor(h / 2))
    newWidth = (int)  (np.floor( w / 2))
    croppedImage = originalImage[160:325, 112:250]
    return croppedImage




ds=pydicom.dcmread('../data/dicom/Knee/vhf.421.dcm')
#plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
img = transformToHu(ds,ds.pixel_array)
imgNoTh = transformToHu(ds,ds.pixel_array)
imgNoTh = imgNoTh -  imgNoTh.min()
num_rows, num_cols = img.shape[:2]
rotation_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), -12, 1)
img_rotation = cv2.warpAffine(img, rotation_matrix, (num_cols, num_rows))
imgNoTh = img_rotation.copy()
imgNoTh = imgNoTh - imgNoTh.min()
imgNoTh = imgNoTh / imgNoTh.max() * 255
originalImage = cropRotulaCT(imgNoTh)

img_rotation_2 = img_rotation.copy()
femur_cropped = cropFemurCT(img_rotation_2)
femur_thresholded = thresholdCTImage(femur_cropped)
originalImage, slope = getLowestPointsFemur(originalImage, femur_thresholded)


rotula_cropped = cropRotulaCT(img_rotation)
rotula_thresholded = thresholdCTImage(rotula_cropped)
originalImage = getTransvesalPointRotula(originalImage, rotula_thresholded, slope)



plt.imshow(img)
plt.show()