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
import json
sys.path.append('../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/')

from PatientHistorial import Patient
from MedicalImage import FemurRotulaImage, TibiaImage
import model

class View:
    def __init__(self):
        self.home_page = builder.get_object("home-page")
        self.new_patient_bt = builder.get_object("hp-b-im")
        self.new_patient_data = builder.get_object("new-patient")
        self.patients_list_window = builder.get_object("patients-list")
        self.pathf1 = builder.get_object("np-tv-p1")
        self.pathf2 = builder.get_object("np-tv-p2")
        self.path_b1 = builder.get_object("np-button-p1")
        self.path_b2 = builder.get_object("np-button-p2")
        self.pathf2_text = ""
        self.pathf1_text = ""

 

    def new_patient_button(self,button):
        self.new_patient_data.show()
        self.home_page.hide()
        self.patients_list_window.hide()

   
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
            self.pathf1_text = dialog.get_filename()
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
            self.pathf2_text = dialog.get_filename()
            buffer.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
             print("Cancel clicked")
        dialog.destroy()
        


    def add_filters(self, dialog):

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def update_list(self):
        list =  builder.get_object("patients")
        list.clear()
        treeview = builder.get_object("tree-list")
        for i, column_title in enumerate(["Nombre", "Apellidos", "Edad", "Sexo"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            treeview.append_column(column)
        data = model.get_patients()
        for i in range(len((data['patients']))):
            list.append( [data['patients'][i]["first_name"], data['patients'][i]["last_name"], str(data['patients'][i]["age"]), data['patients'][i]["sex"]])

    def patients_list(self, button):
        self.home_page.hide()
        self.update_list()
        self.patients_list_window.show()


    def cancel_new_patient(self, button):
        self.new_patient_data.hide()
        self.home_page.show()

    def confirm_new_patient_button(self, button):
        name = builder.get_object("np-fstname")
        last_name = builder.get_object("np-name")
        age = builder.get_object("np-age")
        sex = builder.get_object("np-sex")
        path1 = builder.get_object("np-tv-p1")
        path2 = builder.get_object("np-tv-p2")
        new_patient = Patient(name.get_text(), last_name.get_text(), age.get_text(), sex.get_active_text(), self.pathf1_text, self.pathf2_text)
        model.create_patient(new_patient)
        self.new_patient_data.hide()
        self.update_list()
        self.patients_list_window.show()





bienvenida = builder.get_object("home-page")
bienvenida.connect("delete-event", Gtk.main_quit)
builder.connect_signals(View())
bienvenida.show_all()
Gtk.main()