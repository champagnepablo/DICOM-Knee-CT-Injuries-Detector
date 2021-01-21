import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
from gi.repository.GdkPixbuf import Pixbuf
builder = Gtk.Builder()
builder.add_from_file("interface.glade")
import cv2
import numpy as np
import scipy
import pydicom
import cairo
from PIL import Image
from matplotlib import cm
import sys
import json
sys.path.append('../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/')

from PatientHistorial import Patient
from MedicalImage import FemurRotulaImage, TibiaImage
import meaures
import model
from image_utils import dicom_utils



def create_patient(patient):
    return model.create_patient(patient)


def do_ta_gt(ds, femur_left, femur_right, trochlea, tibia):
    return meaures.ta_gt_measures(ds, femur_left, femur_right, trochlea, tibia)

def refine_ta_gt(ds, points_femur, trochlea, tibia):
    if points_femur[0][1] < points_femur[1][1]:
        femur_left = points_femur[0]
        femur_right = points_femur[1]
    else:
        femur_left = points_femur[1]
        femur_right = points_femur[0]
    if trochlea[0][0][0] < trochlea[0][1][0]:
        points_trochlea = trochlea[0][0]
    else:
        points_trochlea = trochlea[0][1]
    if tibia[0][0][0] < tibia[0][1][0]:
        points_tibia = tibia[0][0]
    else:
        points_tibia = tibia[0][1]
    print(femur_left, femur_right, points_trochlea, points_tibia)
    return meaures.ta_gt_measures(ds, femur_left, femur_right, points_trochlea, points_tibia)

def get_br_result(id, half):
    return model.get_br_result(id, half)

def get_ta_gt_result(id, half):
    return model.get_tagt_result(id, half)

def set_tagt_result(id, result, half):
    return model.set_tagt_result(id, result, half)

def set_br_result(id, result, half):
    return model.set_br_result(id, result, half)



        

    