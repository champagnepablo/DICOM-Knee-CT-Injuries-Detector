import cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt


def cropRotulaCT(originalImage):
    croppedImage = originalImage[146:370, 236:450]
    return croppedImage









img = cv2.imread('../data/img/tatg-r/rodilla.jpg', cv2.IMREAD_COLOR) #read in grayscale mode
img = cropRotulaCT(img)
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = cv2.GaussianBlur(img,(3,3),0)
sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5)  # x
sobely = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=5)  # y
abs_grad_x = cv2.convertScaleAbs(sobelx)
abs_grad_y = cv2.convertScaleAbs(sobely)

grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
plt.imshow(abs_grad_x, cmap = 'gray')
plt.show()