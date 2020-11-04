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
            
def thresholdCTImage(img,c,w):
    window_center = c
    window_width = w
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

def getAngleFemur(frame, contours):
    frame = cv2.cvtColor(frame.astype('float32'), cv2.COLOR_GRAY2BGR)
    for contour in contours:
        #calculate area and moment of each contour
        area = cv2.contourArea(contour)
        M = cv2.moments(contour)

        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])


        #Use contour if size is bigger then 1000 and smaller then 50000
        if area > 1000:
            if area <50000:
                approx = cv2.approxPolyDP(contour, 0.001*cv2.arcLength(contour, True), True)
                #draw contour
                cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)
                #draw circle on center of contour
                cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
                perimeter = cv2.arcLength(contour,True)
                approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
                #fit elipse
                _ ,_ ,angle = cv2.fitEllipse(contour)
                P1x = cX
                P1y = cY
                length = 35

                #calculate vector line at angle of bounding box
                P2x = int(P1x + length * math.cos(math.radians(angle)))
                P2y = int(P1y + length * math.sin(math.radians(angle)))
                 #draw vector line
                cv2.line(frame,(cX, cY),(P2x,P2y),(255,255,255),5)

                #output center of contour
                print  (P1x , P2y, angle)

                #detect bounding box
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                #draw bounding box
                cv2.drawContours(frame, [box],0,(0,0,255),2)


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


def getROI(img):
    img2 = img.copy()
    half_column = img.shape[1] / 2
    for i in range(img.shape[0]-1):
        for j in range(img.shape[1]-1):
            if j> half_column:
                img2[i][j] = 0
    return img2


def rotateFemur(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
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


def getPointsFemur(img, angle):
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


def rotate_rotula(img):
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





#ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/serie/4859838 serie completa.Seq4.Ser4.Img100.dcm')
ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/prueba2.dcm')
#plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
img = transformToHu(ds,ds.pixel_array)
th_img = thresholdCTImage(img,ds.WindowCenter[0] , ds.WindowWidth[0])

roi_img = getROI(th_img)
rotated_img, angle = rotateFemur(roi_img)
cropped_img, (extBot, extBot2) = getPointsFemur(rotated_img, -angle)
img_2d = ds.pixel_array.astype(float)

## Step 2. Rescaling grey scale between 0-255
img_2d_scaled = (np.maximum(img_2d,0) / img_2d.max()) * 255.0

## Step 3. Convert to uint
img_2d_scaled = np.uint8(img_2d_scaled)
print(ds.WindowWidth)
img2 = cv2.cvtColor(img_2d_scaled, cv2.COLOR_GRAY2BGR)
cv2.circle(img2, (extBot[0], extBot[1]), radius=0, color=(0, 0, 255), thickness=-1)
cv2.circle(img2, (extBot2[0], extBot2[1]), radius=0, color=(0, 0, 255), thickness=-1)

rotula_img , (extLeft, extRight) = rotate_rotula(roi_img)

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