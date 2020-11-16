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



#ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/serie/4859838 serie completa.Seq4.Ser4.Img100.dcm')
ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/prueba.dcm')
#plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
img = dicom_utils.transformToHu(ds,ds.pixel_array)
th_img = image_processing.thresholdCTImage(img,ds.WindowCenter[0] , ds.WindowWidth[0])

roi_img = image_processing.getROI(th_img)
rotated_img, angle = image_processing.rotateFemur(roi_img)
cropped_img, (extBot, extBot2) = interesting_points.getPointsFemur(rotated_img, -angle)
img_2d = ds.pixel_array.astype(float)

## Step 2. Rescaling grey scale between 0-255
img_2d_scaled = (np.maximum(img_2d,0) / img_2d.max()) * 255.0

## Step 3. Convert to uint
img_2d_scaled = np.uint8(img_2d_scaled)
print(ds.WindowWidth)
img2 = cv2.cvtColor(img_2d_scaled, cv2.COLOR_GRAY2BGR)
cv2.circle(img2, (extBot[0], extBot[1]), radius=0, color=(0, 0, 255), thickness=-1)
cv2.circle(img2, (extBot2[0], extBot2[1]), radius=0, color=(0, 0, 255), thickness=-1)

rotula_img , (extLeft, extRight) = image_processing.rotate_rotula(roi_img)

cv2.circle(img2, (extLeft[0], extLeft[1]), radius=0, color=(0, 0, 255), thickness=-1)
cv2.circle(img2, (extRight[0], extRight[1]), radius=0, color=(0, 0, 255), thickness=-1)



print(extRight)

'''
num_rows, num_cols = img.shape[:2]
rotation_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), -12, 1)
img_rotation = cv2.warpAffine(img, rotation_matrix, (num_cols, num_rows))
'''
plt.imshow(img2)
plt.show()