#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
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
sys.path.append('../../image-preprocessing/src')
from image_utils import dicom_utils, image_processing, interesting_points


class View:
    def __init__(self):
        self.home_page = builder.get_object("home-page")
        self.new_patient_bt = builder.get_object("hp-b-im")
        self.new_patient_data = builder.get_object("new-patient")
        self.pathf1 = builder.get_object("np-tv-p1")
        self.pathf2 = builder.get_object("np-tv-p2")
        self.path_b1 = builder.get_object("np-button-p1")
        self.path_b2 = builder.get_object("np-button-p2")

 

    def new_patient_button(self,button):
        self.new_patient_data.show()
        self.home_page.hide()

   
    def browse_file_1(self, button):
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
            buffer = self.pathf1.get_buffer()
            buffer.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
             print("Cancel clicked")
        dialog.destroy()
        

    def browse_file_2(self, button):
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
            buffer = self.pathf2.get_buffer()
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



bienvenida = builder.get_object("home-page")
bienvenida.connect("delete-event", Gtk.main_quit)
builder.connect_signals(View())
bienvenida.show_all()
Gtk.main()