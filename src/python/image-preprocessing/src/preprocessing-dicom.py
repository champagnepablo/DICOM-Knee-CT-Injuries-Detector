import math
import cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt
import pydicom
from pydicom.data import get_testdata_files
from pydicom.pixel_data_handlers.util import apply_modality_lut
from pydicom.pixel_data_handlers.util import apply_voi_lut

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
            
def thresholdCTImage(img, window_center, window_width):
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


def getCTContours(originalImage, tresholdedImage):
    contours, _ = cv2.findContours(tresholdedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(originalImage, contours, -1, (0,255,0), 1)
    return originalImage, contours



def getContouredCTImage(originalImage):
    ds = pydicom.dcmread(originalImage)
    hu_scale_image = transformToHu(ds, ds.pixel_array)
    thresholded_ct_image = thresholdCTImage(hu_scale_image)
    contoured_image, contours = getCTContours(hu_scale_image, thresholded_ct_image)
    return contoured_image


ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/serie/4859838 serie completa.Seq4.Ser4.Img100.dcm')
#plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
print(ds.WindowCenter)
img = transformToHu(ds,ds.pixel_array)
img = thresholdCTImage(img, ds.WindowCenter, ds.WindowWidth)
#img2 = ds.pixel_array.copy()    
#getCTContours(img2, img)
plt.imshow(img)
plt.show()