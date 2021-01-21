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

    return img2,extBot, extBot2, throclea_points


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

    cv2.circle(img_left, (extLeft[0], extLeft[1]), radius=0, color=(0, 255, 0), thickness=2)
    cv2.circle(img_left, (extRight[0], extRight[1]), radius=0, color=(0, 255, 0), thickness=2)

    
    return img_left, extBot, extBot2, throclea_points

def get_points_rotula_left(ds):
    img = dicom_utils.transformToHu(ds,ds.pixel_array)
    alt_th = image_processing.thresholdAlternative(img,ds.WindowCenter[0], ds.WindowWidth[0])
    alt_th = alt_th.astype(np.uint8)
    roi_img2 = image_processing.getROI(alt_th)
    roi_img2 = roi_img2.astype(np.uint8)
    points1,points2 = interesting_points.getPointsRotula(roi_img2)
    return points1,points2

def get_points_rotula_right(ds):
    img = dicom_utils.transformToHu(ds,ds.pixel_array)
    alt_th = image_processing.thresholdAlternative(img,ds.WindowCenter[0], ds.WindowWidth[0])
    alt_th = alt_th.astype(np.uint8)
    roi_img2 = image_processing.getROI2(alt_th)
    roi_img2 = roi_img2.astype(np.uint8)
    points1,points2 = interesting_points.getPointsRotula(roi_img2)
    return points1,points2

def get_point_tibia_left(ds):
    img_tibia = dicom_utils.transformToHu(ds,ds.pixel_array)
    img_tibia_norm = dicom_utils.normalizeImage255(img_tibia, ds.WindowCenter[0], ds.WindowWidth[0])
    th_img = image_processing.thresholdAlternative(img_tibia,ds.WindowCenter[0] , ds.WindowWidth[0])
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
    points = [north_west[0], north_west[1]]
    return points

def get_point_tibia_right(ds):
    img_tibia = dicom_utils.transformToHu(ds,ds.pixel_array)
    img_tibia_norm = dicom_utils.normalizeImage255(img_tibia, ds.WindowCenter[0], ds.WindowWidth[0])
    th_img = image_processing.thresholdAlternative(img_tibia,ds.WindowCenter[0] , ds.WindowWidth[0])
    left_image = image_processing.getROI2(th_img)
    left_image = left_image.astype(np.uint8)
    rotated_img, angle = image_processing.rotateFemur(left_image, "right")
    contours, _ = cv2.findContours(rotated_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key = cv2.contourArea, reverse= True)
    north_west = tuple(sorted_contours[0][sorted_contours[0][:, :, 1].argmin()][0])
    transform_points = np.array( [ [ [ north_west[0], north_west[1] ] ]  ])
    h, w = rotated_img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    tf2 = cv2.transform(transform_points, M)
    points = [north_west[0], north_west[1]]
    return tf2[0][0]

def ta_gt_measures(ds, femur_left,femur_right, trochlea, tibia):
    m_femur, b_femur = dicom_utils.getFunctionPoints( femur_left, femur_right)
    m_throclea, b_throclea = dicom_utils.getPerpendicularFunction(m_femur , trochlea)
    m_tibia , b_tibia = dicom_utils.getPerpendicularFunction(m_femur, tibia)
    d = dicom_utils.getDistanceParalelLines(m_throclea, b_throclea, b_tibia)
    print(d/ds.PixelSpacing[0])
    return d/ds.PixelSpacing[0]

def basic_rotulian(ds, femur_left, femur_right, rotula_left, rotula_right):
    m_femur, b_femur = dicom_utils.getFunctionPoints(dicom_utils.mmTranslationPoint(ds.PixelSpacing, femur_left), dicom_utils.mmTranslationPoint(ds.PixelSpacing,femur_right))
    m_rotula, b_rotula = dicom_utils.getFunctionPoints(dicom_utils.mmTranslationPoint(ds.PixelSpacing, rotula_left), dicom_utils.mmTranslationPoint(ds.PixelSpacing,rotula_right))
    tangent_angle = abs((m_femur -m_rotula) /(1 + (m_rotula * m_femur )) )
    angle = np.arctan(tangent_angle)
    angle = angle * 180 / np.pi
    return angle

'''
ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/tibia.dcm')
ds2=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/prueba2.dcm')
tibia = get_point_tibia_left(ds)
hu =dicom_utils.transformToHu(ds2, ds2.pixel_array)
hu2 =dicom_utils.transformToHu(ds, ds.pixel_array)
img, femur_left, femur_right, trochlea = get_points_left(ds2)
d = ta_gt_measures(ds,femur_left, femur_right, trochlea, tibia)
print(trochlea,tibia)

tibia = get_point_tibia_right(ds)


hu =dicom_utils.transformToHu(ds2, ds2.pixel_array)
hu2 =dicom_utils.transformToHu(ds, ds.pixel_array)

img, femur_left, femur_right, trochlea = get_points_right(ds2, hu)
alt_th = image_processing.thresholdAlternative(hu,ds.WindowCenter[0], ds.WindowWidth[0])

alt_th2 = image_processing.thresholdAlternative(hu2,ds.WindowCenter[0], ds.WindowWidth[0])
th = alt_th + alt_th2 
print(trochlea,tibia)

d2 = ta_gt_measures(ds,femur_left, femur_right, trochlea, tibia)

plt.imshow(th)
plt.show()

'''
'''
#ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/serie/4859838 serie completa.Seq4.Ser4.Img100.dcm')

ds2=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/prueba2.dcm')

img_tibia = dicom_utils.transformToHu(ds,ds.pixel_array)
img_femur = dicom_utils.transformToHu(ds2,ds2.pixel_array)

img_tibia_norm = dicom_utils.normalizeImage255(img_tibia, ds.WindowCenter[0], ds.WindowWidth[0])
img_femur_norm = dicom_utils.normalizeImage255(img_femur, ds2.WindowCenter[0], ds2.WindowWidth[0])



th_img = image_processing.thresholdAlternative(img_tibia_norm, ds2.WindowCenter[0], ds2.WindowWidth[0])
th_img_fm = image_processing.thresholdAlternative(img_femur, ds2.WindowCenter[0], ds2.WindowWidth[0])

f = plt.figure()
f.add_subplot(1,2, 1)
plt.imshow(img_femur, cmap='gray')
f.add_subplot(1,2, 2)
plt.imshow(th_img_fm, cmap='gray')
plt.show(block=True)


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


img_tibia_norm_rgb = cv2.cvtColor(img_tibia_norm.astype(np.uint8), cv2.COLOR_GRAY2BGRA)
img_tibia_norm = cv2.bitwise_not(img_tibia_norm)
img_tibia_norm_rgb[:,:,3] = img_tibia_norm
img, femur_left, femur_right, trochlea = get_points_left(ds2)
img2,_,_,_ = get_points_right(ds2, img)


img_femur = dicom_utils.transformToHu(ds2,ds2.pixel_array)
img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
overlay_img = img + img_tibia_norm_rgb

tibia = get_point_tibia_left(ds)

m_femur, b_femur = dicom_utils.getFunctionPoints(dicom_utils.mmTranslationPoint(ds.PixelSpacing, femur_left), dicom_utils.mmTranslationPoint(ds.PixelSpacing,femur_right))
print(ds.PixelSpacing)
m_throclea, b_throclea = dicom_utils.getPerpendicularFunction(m_femur, trochlea)
m_tibia , b_tibia = dicom_utils.getPerpendicularFunction(m_femur, tibia)

d = dicom_utils.getDistanceParalelLines(m_throclea, b_throclea, b_tibia)
print("La distancia TA-GT es : "+ (str) (d) +" mm.")
#cv2.line(img2,(femur_left[0],femur_left[1]),(femur_right[0],femur_right[1]),(255,255,255),1)

y_throclea = m_throclea * trochlea[0] + b_throclea
y_throclea = (int) (y_throclea)

y_tibia = m_tibia * tibia[0] + b_tibia
y_tibia = (int) (y_tibia)

#cv2.line(img2,(trochlea[0],y_throclea),(trochlea[0],trochlea[1]),(255,255,255),1)
#cv2.line(img2,(tibia[0],y_tibia),(tibia[0],tibia[1]),(255,255,255),1)

plt.imshow(img2)

plt.show()

'''