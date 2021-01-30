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
from pydicom.pixel_data_handlers.util import apply_color_lut
import sys
import SimpleITK as sitk
from skimage import exposure # for histogram equalization

sys.path.append('../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/')

from PatientHistorial import Patient
from MedicalImage import FemurRotulaImage, TibiaImage
import meaures
import model, controller
from image_utils import dicom_utils

import os

path = "/home/pablo/Descargas/segundo envío/4546475 TAGT/serie completa"


def listdir(dir):
    filenames = os.listdir(dir)
    if not os.path.exists("prueba"):
        os.mkdir("prueba")
    for files in filenames:
        if files.endswith('.dcm'):
            filePath = path + "/" + files
            ds = pydicom.dcmread(filePath)
            img_2d = ds.pixel_array.astype(float)
            ## Step 2. Rescaling grey scale between 0-255
            img_2d_scaled = (np.maximum(img_2d,0) / img_2d.max()) * 255.0
            ## Step 3. Convert to uint
            img_2d_scaled = np.uint8(img_2d_scaled)
            scale_percent = 150 # percent of original size
            width = int(img_2d_scaled.shape[1] * scale_percent / 100)
            height = int(img_2d_scaled.shape[0] * scale_percent / 100)
            dim = (width, height)
            img_2d_scaled = cv2.resize(img_2d_scaled, dim, interpolation = cv2.INTER_AREA)
            img2 = cv2.cvtColor(img_2d_scaled, cv2.COLOR_GRAY2BGR)
            filename = os.path.splitext(files)[0] + '.png'
            cv2.imwrite("prueba/" + filename, img2)


listdir(path)