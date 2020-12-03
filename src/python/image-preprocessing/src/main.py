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
from image_utils import dicom_utils,image_processing,interesting_points
import SimpleITK as sitk
from skimage import exposure # for histogram equalization




def get_points_left(ds):
    img = dicom_utils.transformToHu(ds,ds.pixel_array)
    th_img = image_processing.thresholdCTImage(img,ds.WindowCenter[0] , ds.WindowWidth[0])
    alt_th = image_processing.thresholdAlternative(img,ds.WindowCenter[0], ds.WindowWidth[0])
    alt_th = alt_th.astype(np.uint8)

    roi_img2 = image_processing.getROI(alt_th)
    roi_img2 = roi_img2.astype(np.uint8)
    roi_img = image_processing.getROI(th_img)
    flood_full = roi_img | roi_img2
    flood_full = flood_full.astype(np.uint8)
    kernel = np.ones((3,2))
    flood_full = cv2.morphologyEx(flood_full, cv2.MORPH_CLOSE, kernel)
    tr_im, throclea_points = interesting_points.getDeepestPointTrochlea(roi_img2, "left")
    rotated_img, angle = image_processing.rotateFemur(roi_img2, "left")
    _, (extBot, extBot2) = interesting_points.getPointsFemur(rotated_img, -angle)
    img_2d = ds.pixel_array.astype(float)

    ## Step 2. Rescaling grey scale between 0-255
    img_2d_scaled = (np.maximum(img_2d,0) / img_2d.max()) * 255.0

    ## Step 3. Convert to uint
    img_2d_scaled = np.uint8(img_2d_scaled)
    img2 = cv2.cvtColor(img_2d_scaled, cv2.COLOR_GRAY2BGR)
    cv2.circle(img2, (extBot[0], extBot[1]), radius=0, color=(0, 0, 255), thickness=2)
    cv2.circle(img2, (extBot2[0], extBot2[1]), radius=0, color=(0, 0, 255), thickness=2)
    _ , (extLeft, extRight) = image_processing.rotate_rotula(roi_img)
   # x,y = interesting_points.getDeepestPointTrochlea(th_img)

    #cv2.circle(img2, (y, x), radius=0, color=(0, 0, 255), thickness=-1)
    cv2.circle(img2, (throclea_points[0], throclea_points[1]), radius=0, color=(255, 0, 0), thickness=2)
    cv2.circle(img2, (extLeft[0], extLeft[1]), radius=0, color=(0, 255, 0), thickness=2)
    cv2.circle(img2, (extRight[0], extRight[1]), radius=0, color=(0, 255, 0), thickness=2)

    return img2,alt_th


def get_points_right(ds, img_left):
    img = dicom_utils.transformToHu(ds,ds.pixel_array)
    th_img = image_processing.thresholdCTImage(img,ds.WindowCenter[0] , ds.WindowWidth[0])
    alt_th = image_processing.thresholdAlternative(img,ds.WindowCenter[0], ds.WindowWidth[0])
    roi_img2 = image_processing.getROI2(alt_th)
    roi_img2 = roi_img2.astype(np.uint8)
    tr_im, throclea_points = interesting_points.getDeepestPointTrochlea(roi_img2)
    roi_img = image_processing.getROI2(th_img)
    rotated_img, angle = image_processing.rotateFemur(roi_img2, "right")
    _, (extBot, extBot2) = interesting_points.getPointsFemur(rotated_img, -angle)
    img_2d = ds.pixel_array.astype(float)

    ## Step 2. Rescaling grey scale between 0-255
    img_2d_scaled = (np.maximum(img_2d,0) / img_2d.max()) * 255.0

    ## Step 3. Convert to uint
    img_2d_scaled = np.uint8(img_2d_scaled)
    img2 = cv2.cvtColor(img_2d_scaled, cv2.COLOR_GRAY2BGR)
    cv2.circle(img_left, (extBot[0], extBot[1]), radius=0, color=(0, 0, 255), thickness=2)
    cv2.circle(img_left, (extBot2[0], extBot2[1]), radius=0, color=(0, 0, 255), thickness=2)
    cv2.circle(img_left, (throclea_points[0], throclea_points[1]), radius=0, color=(255, 0, 0), thickness=2)

    _ , (extLeft, extRight) = image_processing.rotate_rotula(roi_img)

    cv2.circle(img_left, (extLeft[0], extLeft[1]), radius=0, color=(0, 0, 255), thickness=2)
    cv2.circle(img_left, (extRight[0], extRight[1]), radius=0, color=(0, 0, 255), thickness=2)

    return img_left, rotated_img








#ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/serie/4859838 serie completa.Seq4.Ser4.Img100.dcm')
ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/tibia.dcm')
ds2=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/prueba2.dcm')

img_tibia = dicom_utils.transformToHu(ds,ds.pixel_array)
th_img = image_processing.thresholdAlternative(img,ds.WindowCenter[0] , ds.WindowWidth[0])
left_image = image_processing.getROI(th_img)
left_image = left_image.astype(np.uint8)
rotated_img, angle = image_processing.rotateFemur(left_image, "left")
contours, _ = cv2.findContours(rotated_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
sorted_contours = sorted(contours, key = cv2.contourArea, reverse= True)
north_west = tuple(sorted_contours[0][sorted_contours[0][:, :, 1].argmin()][0])
transform_points = np.array( [ [ [ north_west[0], north_west[1] ] ]  ])
h, w = rotated_img.shape[:2]
center = (w // 2, h // 2)
M = cv2.getRotationMatrix2D(center, angle, 1.0)
tf2 = cv2.transform(transform_points, M)


img, th_img = get_points_left(ds2)
img2,th_img2 = get_points_right(ds2, img)

img_femur = dicom_utils.transformToHu(ds,ds.pixel_array)



'''
num_rows, num_cols = img.shape[:2]
rotation_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), -12, 1)
img_rotation = cv2.warpAffine(img, rotation_matrix, (num_cols, num_rows))
'''


plt.imshow(img)

plt.show()
