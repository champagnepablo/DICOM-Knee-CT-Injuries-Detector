#!/usr/bin/env python3

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
import os
sys.path.append('../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/')

from PatientHistorial import Patient
from MedicalImage import FemurRotulaImage, TibiaImage
import meaures
import model
from image_utils import dicom_utils
class View:
    def __init__(self):
        self.home_page = builder.get_object("home-page")
        self.new_patient_bt = builder.get_object("hp-b-im")
        self.new_patient_data = builder.get_object("new-patient")
        self.patients_list_window = builder.get_object("patients-list")
        self.choose_action_window = builder.get_object("choose-action-window")
        self.patient_added_confirmation = builder.get_object("patient-added-confirmation")
        self.measurements_details_window = None
        self.tagt_details_window = builder.get_object("tagt-details-window")
        self.print_lines_br_window = builder.get_object("print-lines-br-window")
        self.pathf1 = builder.get_object("np-tv-p1")
        self.pathf2 = builder.get_object("np-tv-p2")
        self.path_b1 = builder.get_object("np-button-p1")
        self.path_b2 = builder.get_object("np-button-p2")
        self.pathf2_text = ""
        self.pathf1_text = ""
        self.coordinates_list = []
        self.original_image = cv2.imread('messi.jpg')
        self.clone = self.original_image.copy()
        self.line1 = []
        self.line2 = []
        self.line3 = []
        self.reset1 = False 
        self.reset2 = False
        self.reset3 = False



 

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
        data = model.get_patients()
        list =  builder.get_object("patients")
        list.clear()
        for i in range(len((data['patients']))):
            list.append([str(data['patients'][i]["patient_id"]), data['patients'][i]["first_name"], data['patients'][i]["last_name"], str(data['patients'][i]["age"]), data['patients'][i]["sex"]])

    def patients_list(self, button):
        self.home_page.hide()
        treeview = builder.get_object("tree-list")
        for i, column_title in enumerate(["DNI","Nombre", "Apellidos", "Edad", "Sexo"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            treeview.append_column(column)
        self.update_list()
        self.patients_list_window.show()


    def cancel_new_patient(self, button):
        self.new_patient_data.hide()
        self.home_page.show()

    def confirm_new_patient_button(self, button):
        id = builder.get_object("np-dni")
        name = builder.get_object("np-fstname")
        last_name = builder.get_object("np-name")
        age = builder.get_object("np-age")
        sex = builder.get_object("np-sex")
        path1 = builder.get_object("np-tv-p1")
        path2 = builder.get_object("np-tv-p2")
        new_patient = Patient(id.get_text(), name.get_text(), last_name.get_text(), age.get_text(), sex.get_active_text(), self.pathf1_text, self.pathf2_text)
        model.create_patient(new_patient)
        self.current_patient = new_patient
        self.new_patient_data.hide()
        self.update_list()
        self.choose_action_window.show()

    def added_new_patient_window(self,button):
        self.choose_action_window.hide()
        self.patients_list_window.show()
    
    def hide_dialog_confirm(self, button):
        self.patient_added_confirmation.hide()

    def do_ta_gt(self,button):
        selection = builder.get_object("tagtd-options").get_active_text()
        self.tagt_details_window.hide()
        print(selection)
        print("Doing ta-gt")
        img, _, _, _ = meaures.get_points_left(self.current_patient.femurRotulaImage.ds)
      #  cv2.imshow("Image", img)
        cv2.imwrite('image.png',img)
        #window = builder.get_object("tagt-panel")
        self.measurements_details_window = builder.get_object("tagt-result")
        tagt_img = builder.get_object("tagt-img")
        dni = builder.get_object("tagtr-dni")
        dni.set_text(self.current_patient.id)
        fst_name = builder.get_object("tagtr-fstname")
        fst_name.set_text(self.current_patient.firstName)
        name = builder.get_object("tagtr-name")
        name.set_text(self.current_patient.name)
        age = builder.get_object("tagtr-age")
        age.set_text(str(self.current_patient.age))
        sex = builder.get_object("tagtr-sex")
        sex.set_text(self.current_patient.sex)
        tagt_img.set_from_file("image.png")
        self.measurements_details_window.show()
        if os.path.exists("image.png"):
            os.remove("image.png")

    def tagt_details_button(self,button):
        window = builder.get_object("tagt-details-window")
        self.choose_action_window.hide()    
        window.show()

    def do_other_measurements_button(self,button):
        self.measurements_details_window.hide()
        self.measurements_details_window = None
        self.choose_action_window.show()

    def store_bd_button(self,button):
        print("funciona")
        
    def print_lines_br_window_button(self,button):
        self.print_lines_br_window.show()
    
    def confirm_patient_added_dialog(self, button):
        self.choose_action_window.hide()
        self.patient_added_confirmation.show()
        self.patients_list_window.show()

        def get_points(im):
            # Set up data to send to mouse handler
            data = {}
            data['im'] = im.copy()
            data['lines'] = []

            # Set the callback function for any mouse event
            cv2.imshow("Image", im)
            cv2.setMouseCallback("Image", mouse_handler, data)
            cv2.waitKey(0)

            # Convert array to np.array in shape n,2,2
            points = np.uint16(data['lines'])

            return points, data['im']
    

    def extract_coordinates(self, event, x, y, flags, parameters):
    # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x,y)]

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x,y))
            print('Starting: {}, Ending: {}'.format(self.image_coordinates[0], self.image_coordinates[1]))
            if len(self.coordinates_list) == 3:
                print("Finished")
            # Draw line
            if ((self.line1)  == [] and self.reset1 == True):
                cv2.line(self.clone, self.image_coordinates[0], self.image_coordinates[1], (36,255,12), 2)
                self.line1.append((self.image_coordinates[0], self.image_coordinates[1]))
                self.reset1 = False
                print("printa linea1")
            elif ((self.line2)  == [] and self.reset2 == True):
                cv2.line(self.clone, self.image_coordinates[0], self.image_coordinates[1], (36,255,12), 2)
                self.line2.append((self.image_coordinates[0], self.image_coordinates[1]))
                self.reset2 = False
                print("printa linea2 ")
            elif ((self.line3) == [] and self.reset3 == True):
                cv2.line(self.clone, self.image_coordinates[0], self.image_coordinates[1], (36,255,12), 2)
                self.line3.append((self.image_coordinates[0], self.image_coordinates[1]))
                self.reset3 = False
                print("printa linea3")
            cv2.imshow("image", self.clone) 

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.original_image.copy()

    def show_image(self):
        return self.clone

    def print_lines_window(self,button):
        # List to store start/end points
        self.image_coordinates = []
        print_lines_window = builder.get_object("print-lines-window")
        print_lines_window.show()
    



    
    def set_line1(self,button):
        cv2.destroyAllWindows()
        copy = cv2.imread('messi.jpg')
        self.clone = copy
        print(self.line2)
        if  (self.line2) != [] :
            cv2.line(copy, self.line2[0][0], self.line2[0][1], (36,255,12), 2)
        if  (self.line3) != [] :
            cv2.line(copy, self.line3[0][0], self.line3[0][1], (36,255,12), 2)
        screen_res = 1980, 1080 
        scale_width = screen_res[0] / copy.shape[1]
        scale_height = screen_res[1] / copy.shape[0]
        scale = min(scale_width, scale_height)
        window_width = int(copy.shape[1] * scale)
        window_height = int(copy.shape[0] * scale)
        cv2.namedWindow("image", cv2.WINDOW_GUI_EXPANDED)
        cv2.moveWindow("image", 40,30)
        cv2.imshow('image',copy)
       
        self.reset1 = True
        self.line1 = []
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.extract_coordinates)

    def set_line2(self,button):
        copy = cv2.imread('messi.jpg')
        self.clone = copy
        if  (self.line1) != [] :
            cv2.line(copy, self.line1[0][0], self.line1[0][1], (36,255,12), 2)
        if  (self.line3) != [] :
            cv2.line(copy, self.line3[0][0], self.line3[0][1], (36,255,12), 2)
        cv2.imshow('image',copy)
        self.line2 = []
        self.reset2 = True
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.extract_coordinates)

    def set_line3(self,button):
        cv2.destroyAllWindows()
        copy = cv2.imread('messi.jpg')
        if  (self.line1) != [] :
            cv2.line(copy, self.line1[0][0], self.line1[0][1], (36,255,12), 2)
        if  (self.line2) != [] :
            cv2.line(copy, self.line2[0][0], self.line2[0][1], (36,255,12), 2)
        self.clone = copy
        cv2.imshow('image',copy)
        self.line3 = []
        self.reset3 = True
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.extract_coordinates)

    def delete_patient(self, button):
        selection = builder.get_object("tree-list").get_selection()
        selection.set_mode(Gtk.SelectionMode.BROWSE)
        (model,paths) = selection.get_selected_rows()
        if len(paths)==1:
            for path in paths:
                tree_iter = model.get_iter(path)
                self.rowselected = model.get_value(tree_iter,0)
        confirm_delete = builder.get_object("confirm_delete_window")
        confirm_delete.show()

    def cancel_delete_patient(self,button):
        confirm_delete = builder.get_object("confirm_delete_window")
        confirm_delete.hide()

    def confirm_delete_patient(self,button):
        model.remove_patient(self.rowselected)
        self.update_list()
        confirm_delete = builder.get_object("confirm_delete_window")
        confirm_delete.hide()   

    def show_ta_gt(self, button):
        return 0







bienvenida = builder.get_object("home-page")
bienvenida.connect("delete-event", Gtk.main_quit)
builder.connect_signals(View())
bienvenida.show_all()
Gtk.main()