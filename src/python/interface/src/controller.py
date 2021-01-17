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



class Controller():
    def  __init__(self):
        self.model = Model()
        

    