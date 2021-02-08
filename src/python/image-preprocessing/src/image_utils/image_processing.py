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
            if j > half_column or i > img.shape[0]:
                img2[i][j] = 0
    return img2

def getROI2(img):
    """
    Crops the ROI of the CT image

    :param originalImage: image to be cropped
    """

    img2 = img.copy()
    half_column = img.shape[1] / 2
    for i in range(img.shape[0]-1):
        for j in range(img.shape[1]-1):
            if j < half_column or i > img.shape[0]:
                img2[i][j] = 0
    return img2



def rotateFemur(img, half = "left"):
    """
    Rotates image in a way which Femur bone is pararel to the margins of the image
    
    :param img: image to be rotated
    """
    angle = getAngle(img)
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    if half == "right":
        angle = -angle
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h),
    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE) 
    angle2 = getAngle(rotated)
    if abs(angle2) != 0:
        rotated = adjustRotating(rotated, -angle)    
  #  cv2.drawContours(img, [biggest_contour], 0, (0,255,0), 3)
    return rotated, -angle



def rotateRotula(img, half = "left"):
    """
    Rotates image in a way which Femur bone is pararel to the margins of the image
    
    :param img: image to be rotated
    """
    angle = getAngle(img)
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    if half == "right":
        angle = -angle
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h),
    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE) 
    angle2 = getAngleRotula(rotated)
    if abs(angle2) != 0:
        rotated = adjustRotating(rotated, -angle)    
  #  cv2.drawContours(img, [biggest_contour], 0, (0,255,0), 3)
    return rotated, -angle

def getAngle(img):
    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
    rect = cv2.minAreaRect(biggest_contour)
    angle = rect[2]
    if angle < -45:
        angle = (90 + angle)
    else:
        angle = -angle
    return angle

def getAngleRotula(img):
    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse= True)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    biggest_contour = contour_sizes[0][1][1]
    rect = cv2.minAreaRect(biggest_contour)
    angle = rect[2]
    if angle < -45:
        angle = (90 + angle)
    else:
        angle = -angle
    return angle




def adjustRotating(img, angle):
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    angle = 2 * angle
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h),
    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE) 
    return rotated

  #  cv2.drawContours(img, [biggest_contour], 0, (0,255,0), 3)
    return rotated, -angle

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



def setAlphaChannel(img, mask):
    """
    Converts an normal image into a RGBA image

    :param img: Input image
    """

    mask = [pixel * 255 for pixel in mask]
    rgba_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    rgba_img[:, :, 3] = mask
    return rgba_img


def remove_rotula(th_img, femur_contour):
    removed_img = th_img.copy()
    north = tuple(femur_contour[femur_contour[:, :, 1].argmax()][0])
    for i in range(th_img.shape[0]):
        for j in range(th_img.shape[1]):
            if i < north[1]:
                removed_img[i][j] = 0

    return removed_img


def new_method_segmentation(img):
    v_min = np.amin(img)
    v_max = np.amax(img)
    t_new = (v_max + v_min) // 2
    t_old = 0
    background_img = np.zeros((img.shape[0], img.shape[1]))
    foreground_img = np.zeros((img.shape[0], img.shape[1]))
    while (t_new != t_old):
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i][j] < t_new :
                    background_img[i][j] = img[i][j]
                else :
                    foreground_img[i][j] = img[i][j]
        mean_back = np.sum(np.sum(background_img))
        mean_fore = np.sum(np.sum(np.sum(foreground_img)))
        non_zero_back = np.count_nonzero(background_img)
        non_zero_fore = np.count_nonzero(foreground_img)

        mean_back = mean_back // non_zero_back
        mean_fore = mean_fore // non_zero_fore

        t_old = t_new
        t_new = (mean_fore + mean_fore) // 2
    

    return foreground_img

def thresholdAlternative(img, WindowCenter, WindowWidth):
    norm_img = dicom_utils.normalizeImage255(img,  WindowCenter, WindowWidth)
    blurred = cv2.GaussianBlur(norm_img, (5,5),0)
    im_th = new_method_segmentation(blurred)
    im_th_2 = new_method_segmentation(norm_img)
    im_th[im_th > 0] = 1
    
    im_th_2[im_th_2 > 0] = 1

    kernel = np.ones((5,3), dtype = np.uint8)
    closing = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel)

    diff =  cv2.bitwise_or(closing, im_th_2)
    diff = diff.astype(np.uint8)
    im_floodfill = diff.copy()
    h, w = diff.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(im_floodfill, mask, (74,291), 255)
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    im_out = diff | im_floodfill_inv
    return im_th


def floodfillContour(contourImage):
    h, w = contourImage.shape[:2]
    flood_mask = np.zeros((h+2, w+2), dtype=np.uint8)
    connectivity = 8
    flood_fill_flags = (connectivity | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | 255 << 8) 

    # Copy the image.
    im_floodfill = contourImage.copy()

    # Floodfill from point inside arena, not inside a black dot
    cv2.floodFill(im_floodfill, flood_mask, (h//2 + 20, w//2 + 20), 255, None, None, flood_fill_flags)

    borders = []
    for i in range(len(contourImage)):
        borders.append([B-A for A,B in zip(contourImage[i], flood_mask[i])])

    borders = np.asarray(borders)
    borders = cv2.bitwise_not(borders)
    return flood_mask


def getDrawedImageTAGT(img, femur_left, femur_right, trochlea, tibia):
    m, _ = dicom_utils.getFunctionPoints(femur_left, femur_right)
    m2, b2 = dicom_utils.getPerpendicularFunction(m, trochlea)
    m3, b3 = dicom_utils.getPerpendicularFunction(m, tibia)
    x_trochlea = int ((femur_left[1] + 20 - b2) / m2)
    x_tibia = int ((femur_left[1] + 20 - b3) / m3)
    cv2.line(img, (femur_left[0], femur_left[1]), (femur_right[0], femur_right[1]), color=(255,255,255), thickness=1)
    cv2.line(img,  (x_trochlea, femur_left[1] + 20), (trochlea[0], trochlea[1]),  color=(255,255,255), thickness=1)
    cv2.line(img,  (x_tibia, femur_left[1] + 20), (tibia[0], tibia[1]),  color=(255,255,255), thickness=1)
    lines = [[(femur_left[0], femur_left[1]), (femur_right[0], femur_right[1])], [(x_trochlea, femur_left[1] + 20), (trochlea[0], trochlea[1])], [(x_tibia, femur_left[1] + 20), (tibia[0], tibia[1])]]
    return img, lines

def getDrawedImageBR(img, femur_left, femur_right, rotula_left, rotula_right):
    cv2.line(img, (femur_left[0], femur_left[1]), (femur_right[0], femur_right[1]), color=(255,255,255), thickness=1)
    cv2.line(img, (rotula_left[0], rotula_left[1]), (rotula_right[0], rotula_right[1]), color=(255,255,255), thickness=1)
    lines = [[(femur_left[0], femur_left[1]), (femur_right[0], femur_right[1])], [(rotula_left[0], rotula_left[1]), (rotula_right[0], rotula_right[1])]]
    return img, lines






