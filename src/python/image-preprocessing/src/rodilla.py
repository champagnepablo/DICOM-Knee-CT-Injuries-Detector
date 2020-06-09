import cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt



def colorAdjustment(image):
    #grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(image, 11, 17, 17)
   # edged = cv2.Canny(gray , 10, 250)
    kernel = np.ones((5,5),np.uint8)
    erosion = cv2.erode(gray,kernel,iterations = 1)
    edges = cv2.Canny(erosion,80,150)
    return edges

    




def processImage(image):
    img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    img =  colorAdjustment(img)
    return img


img = processImage('rodilla4.jpeg')

plt.imshow(img, cmap = 'gray')
plt.show()