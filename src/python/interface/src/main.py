#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
builder = Gtk.Builder()
builder.add_from_file("home.glade")
import cv2
import numpy as np
import scipy
import pydicom
import cairo
from PIL import Image
from matplotlib import cm
import sys
sys.path.append('../../image-preprocessing/src')
from image_utils import dicom_utils, image_processing, interesting_points


def click_event(event, x, y, flags, params): 
  
    # checking for left mouse clicks 
    if event == cv2.EVENT_LBUTTONDOWN: 
  
        # displaying the coordinates 
        # on the Shell 
        print(x, ' ', y) 
  
        # displaying the coordinates 
        # on the image window 
        font = cv2.FONT_HERSHEY_SIMPLEX 
  
    # checking for right mouse clicks      
    if event==cv2.EVENT_RBUTTONDOWN: 
  
        # displaying the coordinates 
        # on the Shell 
        print(x, ' ', y) 
  
        # displaying the coordinates 
        # on the image window 
        font = cv2.FONT_HERSHEY_SIMPLEX 
        print(x,y)
class View:
    def __init__(self):
        self.home_page = builder.get_object("home-page")
        self.med_im = builder.get_object("medim")
        self.pathf1 = builder.get_object("home-path1")
        self.pathf2 = builder.get_object("home-path2")
        self.medim1 = builder.get_object("medim-photo1")
        self.medim2 = builder.get_object("medim-2")
    
    def browse_file(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=None, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            buffer = self.pathf1.get_buffer()
            buffer.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)



    def ok_button(self, button):
        medim = builder.get_object("medim")
        builder.get_object("home-page").hide()
        ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/tibia.dcm')
        img_at = cv2.imread("/home/pablo/Documentos/TFG/src/python/interface/atl.png")
        img_hu = dicom_utils.transformToHu(ds,ds.pixel_array)
        normalized_img = dicom_utils.normalizeImage255(img_hu, ds.WindowCenter[0], ds.WindowWidth[0])
        arr = np.array(normalized_img)
        pillowimage = Image.fromarray(normalized_image)
        glibbytes = GLib.Bytes.new( pillowimage.tobytes() )
        gdkpixbuf = GdkPixbuf.Pixbuf.new_from_data( glibbytes.get_data(), GdkPixbuf.Colorspace.RGB, False, 8, pillowimage.width, pillowimage.height, len( pillowimage.getbands() )*pillowimage.width, None, None )
        self.medim1.set_from_pixbuf(gdkpixbuf)
        #self.medim1.set_from_file("/home/pablo/Documentos/TFG/src/python/interface/atl.png")
        medim.show()
    '''
        img = cv2.imread("/home/pablo/Documentos/TFG/src/python/interface/atl.png")
        ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/tibia.dcm')
        cv2.imshow('image', ds.pixel_array) 
        cv2.setMouseCallback('image', click_event) 
  
    # wait for a key to be pressed to exit 
        cv2.waitKey(0) 
  
    # close the window 
        cv2.destroyAllWindows() 
        medim.show()
'''
bienvenida=builder.get_object("home-page")
bienvenida.connect("delete-event",Gtk.main_quit)
builder.connect_signals(View())
bienvenida.show_all()
Gtk.main()
