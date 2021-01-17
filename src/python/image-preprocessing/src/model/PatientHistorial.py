import sys
sys.path.insert(1, '../../src')
import pydicom
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
from MedicalImage import FemurRotulaImage, TibiaImage


class Patient:
    def __init__(self, id, firstName, name, age, sex, dcmfile1, dcmfile2):
        self.id = id
        self.firstName = firstName
        self.name = name
        self.age = age
        self.sex = sex
        self.femurRotulaImage = FemurRotulaImage(dcmfile1)
        self.tibiaImage = TibiaImage(dcmfile2)
