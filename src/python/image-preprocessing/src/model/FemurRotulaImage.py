import sys
sys.path.append('../')
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
import MedicalImage

class FemurRotulaImage(MedicalImage):
    def __init__(self, dcmfile):
        ds = pydicom.dcmread(dcmfile)
        self.originalImage = ds.pixel_array
        if type(ds.WindowCenter) == pydicom.multival.MultiValue:
             self.WindowCenter = ds.WindowCenter[0]
        else:
            self.WindowCenter = ds.WindowCenter
        if type(ds.WindowWidth) == pydicom.multival.MultiValue:
            self.WindowWidth = ds.WindowWidth[0]
        else:
            self.WindowWidth = ds.WindowWidth
        self.PixelSpacing = ds.PixelSpacing
        self.RescaleSlope = ds.RescaleSlope
        self.RescaleIntercept = ds.RescaleIntercept
        self.huImage = dicom_utils.transformToHu(ds, ds.pixel_array)
        self.contourImage = image_processing.thresholdAlternative(self.huImage, self.WindowCenter, self.WindowWidth)

