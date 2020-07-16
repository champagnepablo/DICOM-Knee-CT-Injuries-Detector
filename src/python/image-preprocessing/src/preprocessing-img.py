import cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt



def colorAdjustment(image):
    #grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(image)
    image = cv2.medianBlur(image, 3)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(10, 10))
    c = clahe.apply(gray)
    ret,binary = cv2.threshold(c, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    return binary

    
def color2(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.equalizeHist(gray)
    ret,binary = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    grad_x = cv2.Sobel(binary,cv2.CV_64F,1,0,ksize=5)  # x
    grad_y = cv2.Sobel(binary,cv2.CV_64F,0,1,ksize=5)  # y
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)


    return grad




def processImage(image):
    img = cv2.imread(image, cv2.IMREAD_COLOR) #read in grayscale mode
    print(img)
    img =  colorAdjustment(img)
    return img


img = processImage('rodilla3.png')

plt.imshow(img, cmap = 'gray')
plt.show()