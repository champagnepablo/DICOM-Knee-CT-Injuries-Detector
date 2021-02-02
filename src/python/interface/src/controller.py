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
import os.path
from os import path
import export_serie_to_png
sys.path.append('../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/')

from PatientHistorial import Patient
from MedicalImage import FemurRotulaImage, TibiaImage
import meaures
import model
from image_utils import dicom_utils, image_processing



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

def check_patient_data(id, name, last_name, age, pathserie):
    if id == "":
        return False
    if name == "":
        return False
    if last_name == "":
        return False
    try :
        an_integer = int(age)
    except ValueError:
        return False
    if pathserie == "" or path.isdir(pathserie) == False:
        return False
    return True
        
def exportSerieToPng(dir):
    export_serie_to_png.listdir(dir)

def pngPathToDCM(file, path):
    path_dcm = file.replace('.png', '.dcm')
    path_dcm = path_dcm.replace('prueba/',  path + '/')
    return path_dcm

def removePngSeries():
    filenames = os.listdir("prueba/")
    for files in filenames:
        path = "prueba/" + files
        os.remove(path)

def exportDStoPNG(ds):
    return export_serie_to_png.exportDStoPNG(ds)

def getMeasures(measure, half, patient):
    if measure == "TA-GT":
        if half == "Izquierda":
            femur_left, femur_right, trochlea = meaures.get_points_left(patient.femurRotulaImage.ds)
            tibia = meaures.get_point_tibia_left(patient.tibiaImage.ds)
        elif half == "Derecha":
            femur_left, femur_right, trochlea = meaures.get_points_right(patient.femurRotulaImage.ds)
            tibia = meaures.get_point_tibia_right(patient.tibiaImage.ds)
        d = meaures.ta_gt_measures(patient.femurRotulaImage.ds, femur_left, femur_right, trochlea, tibia)
        d = float(round(d, 2))
        ds = patient.femurRotulaImage.originalImage + patient.tibiaImage.originalImage
        img = export_serie_to_png.exportDStoPNG(ds)
        img, lines = image_processing.getDrawedImageTAGT(img, femur_left, femur_right, trochlea, tibia)
        return d, img, lines
    elif measure == "Básica Rotuliana":
        if half == "Izquierda":
            femur_left, femur_right, trochlea = meaures.get_points_left(patient.femurRotulaImage.ds)
            rotula = meaures.get_points_rotula_left(patient.femurRotulaImage.ds)
            angle = meaures.basic_rotulian(patient.femurRotulaImage.ds, femur_left, femur_right, rotula[0], rotula[1])
            angle = float(round(angle, 2))
            img = export_serie_to_png.exportDStoPNG(patient.femurRotulaImage.originalImage)
            img, lines = image_processing.getDrawedImageBR(img, femur_left, femur_right,rotula[0], rotula[1])
            return angle, img,lines
        elif half == "Derecha":
            femur_left, femur_right, trochlea = meaures.get_points_right(patient.femurRotulaImage.ds)
            rotula = meaures.get_points_rotula_right(patient.femurRotulaImage.ds)
            angle = meaures.basic_rotulian(patient.femurRotulaImage.ds, femur_left, femur_right, rotula[0], rotula[1])
            angle = float(round(angle, 2))            
            img = export_serie_to_png.exportDStoPNG(patient.femurRotulaImage.originalImage)
            img, lines = image_processing.getDrawedImageBR(img, femur_left, femur_right, rotula[0], rotula[1])
            return angle, img, lines


def refineMeasure(measure, lines, patient):
    if measure == "TA-GT":
        femur_left = lines[0][0]
        femur_right = lines[0][1]
        trochlea = lines[1][1]
        tibia = lines[2][1]
        d = meaures.ta_gt_measures(patient.femurRotulaImage.ds, femur_left, femur_right, trochlea, tibia)
        d = float(round(d, 2))
        ds = patient.femurRotulaImage.originalImage + patient.tibiaImage.originalImage
        img = export_serie_to_png.exportDStoPNG(ds)
        img, lines = image_processing.getDrawedImageTAGT(img, femur_left, femur_right, trochlea, tibia)
        return str(d), img
    elif measure == "Básica Rotuliana":
        femur_left = lines[0][0]
        femur_right = lines[0][1]
        rotula_left = lines[1][0]
        rotula_right = lines[1][1]
        angle = meaures.basic_rotulian(patient.femurRotulaImage.ds, femur_left, femur_right, rotula_left, rotula_right)
        angle = float(round(angle, 2))
        img = export_serie_to_png.exportDStoPNG(patient.femurRotulaImage.originalImage)
        img, lines = image_processing.getDrawedImageBR(img, femur_left, femur_right, rotula_left, rotula_right)
        return angle. img


def storeTAGTResult(patient, result, half):
    if half == "Izquierda":
        model.set_tagt_result(patient.id, result, "left")
    else:
        model.set_tagt_result(patient.id, result, "right")


def storeBRResult(patient, result, half):
    if half == "Izquierda":
        model.set_br_result(patient.id, result, "left")
    else:
        model.set_br_result(patient.id, result, "right")
        

def getStoredTAGTResult(patient, half):
    if half == "Izquierda":
        return model.get_tagt_result(patient.id, "left")
    else:
        return model.get_tagt_result(patient.id, "right")
    
def getStoredBRResult(patient, half):
    if half == "Izquierda":
        return model.get_br_result(patient.id, "left")
    else:
        return model.get_br_result(patient.id, "right")


def findPatient(patient):
    return model.find_patient(patient.id)