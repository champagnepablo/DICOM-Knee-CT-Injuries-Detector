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
    roi_img = image_processing.getROI(th_img)
    roi_img2 = roi_img.copy()
    rotated_img, angle = image_processing.rotateFemur(roi_img, "left")
    _, (extBot, extBot2) = interesting_points.getPointsFemur(rotated_img, -angle)
    tr_im, throclea_points = interesting_points.getDeepestPointTrochlea(roi_img2)
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
    #print(x,y)
    #cv2.circle(img2, (y, x), radius=0, color=(0, 0, 255), thickness=-1)
    print(throclea_points)
    cv2.circle(img2, (throclea_points[0], throclea_points[1]), radius=0, color=(255, 0, 0), thickness=2)
    cv2.circle(img2, (extLeft[0], extLeft[1]), radius=0, color=(0, 255, 0), thickness=2)
    cv2.circle(img2, (extRight[0], extRight[1]), radius=0, color=(0, 255, 0), thickness=2)

    return img2,rotated_img


def get_points_right(ds, img_left):
    img = dicom_utils.transformToHu(ds,ds.pixel_array)
    th_img = image_processing.thresholdCTImage(img,ds.WindowCenter[1] , ds.WindowWidth[0])

    roi_img = image_processing.getROI2(th_img)
    rotated_img, angle = image_processing.rotateFemur(roi_img, "right")
    _, (extBot, extBot2) = interesting_points.getPointsFemur(rotated_img, -angle)
    img_2d = ds.pixel_array.astype(float)

    ## Step 2. Rescaling grey scale between 0-255
    img_2d_scaled = (np.maximum(img_2d,0) / img_2d.max()) * 255.0

    ## Step 3. Convert to uint
    img_2d_scaled = np.uint8(img_2d_scaled)
    img2 = cv2.cvtColor(img_2d_scaled, cv2.COLOR_GRAY2BGR)
    cv2.circle(img_left, (extBot[0], extBot[1]), radius=0, color=(0, 0, 255), thickness=-1)
    cv2.circle(img_left, (extBot2[0], extBot2[1]), radius=0, color=(0, 0, 255), thickness=-1)

    _ , (extLeft, extRight) = image_processing.rotate_rotula(roi_img)

    cv2.circle(img_left, (extLeft[0], extLeft[1]), radius=0, color=(0, 0, 255), thickness=-1)
    cv2.circle(img_left, (extRight[0], extRight[1]), radius=0, color=(0, 0, 255), thickness=-1)

    return img_left








#ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/serie/4859838 serie completa.Seq4.Ser4.Img100.dcm')
ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/prueba4.dcm')
#plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
img, th_img = get_points_left(ds)
img2 = get_points_right(ds, img)
img3 = dicom_utils.transformToHu(ds,ds.pixel_array)
#img4 = image_processing.setAlphaChannel(img,th_img)


'''
num_rows, num_cols = img.shape[:2]
rotation_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), -12, 1)
img_rotation = cv2.warpAffine(img, rotation_matrix, (num_cols, num_rows))
'''



plt.imshow(img2)
plt.show()
