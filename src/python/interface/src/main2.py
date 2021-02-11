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
import sys
import json
import os
import pydicom
import math
import string

sys.path.append('../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/')

from PatientHistorial import Patient
from MedicalImage import FemurRotulaImage, TibiaImage
import meaures
import model, controller
from image_utils import dicom_utils
class View:
    def __init__(self):
        self.home_page = builder.get_object("home-page")
        self.new_patient_bt = builder.get_object("hp-b-im")
        self.new_patient_data = builder.get_object("new-patient")
        self.patients_list_window = builder.get_object("patients-list")
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
        self.interesting_points = [[ (10,30), (50, 200) ], [ (67, 43), (200, 154) ], [ (152, 101), (45, 104) ]]




 

    def new_patient_button(self,button):
        self.new_patient_data.show()
        self.new_patient_data.connect("delete-event", Gtk.main_quit)
        self.new_patient_data.set_title("Añadir nuevo estudio")
        self.home_page.hide()
        self.patients_list_window.hide()
        
    def on_folder_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Seleccione la carpeta donde se encuentra el estudio DICOM",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
          "Cancelar", Gtk.ResponseType.CANCEL, "Seleccionar", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            buffer = self.pathf2.get_buffer()
            self.pathf2_text = dialog.get_filename()
            buffer.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()


        dialog.destroy()


    def add_filters(self, dialog):

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def update_list(self):
        data = controller.get_patients()
        list =  builder.get_object("patients")
        list.clear()
        for i in range(len((data['patients']))):
            list.append([str(data['patients'][i]["patient_id"]), data['patients'][i]["first_name"], data['patients'][i]["last_name"], str(data['patients'][i]["age"]), data['patients'][i]["sex"]])

    def patients_list(self, button):
        builder.get_object("patients-list").set_title("Listado de estudios")
        builder.get_object("patients-list").connect("delete-event", Gtk.main_quit)
        self.home_page.hide()
        treeview = builder.get_object("tree-list")
        for i, column_title in enumerate(["DNI","Nombre", "Apellidos", "Fecha de Nacimiento", "Sexo"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            treeview.append_column(column)
        self.update_list()
        self.patients_list_window.show()


    def cancel_new_patient(self, button):
        self.new_patient_data.hide()
        self.home_page.show()

    def confirm_new_patient_button(self, button):
        self.id = builder.get_object("np-dni")
        self.name = builder.get_object("np-fstname")
        self.last_name = builder.get_object("np-name")
        self.day = builder.get_object("np-day")
        self.month = builder.get_object("np-month")
        self.year = builder.get_object("np-year")
        if controller.check_date(int(self.day.get_text()), int(self.month.get_text()), int(self.year.get_text())) == True: 
            self.age = self.day.get_text() + "/"+ self.month.get_text() + "/" + self.year.get_text()
        else :
            self.age = ""
        self.sex = builder.get_object("np-sex")
        self.path2 = builder.get_object("np-tv-p2")
        if controller.check_patient_data(self.id.get_text(), self.name.get_text(), self.last_name.get_text(), self.age, self.pathf2_text) == False:
            builder.get_object("check-data-patient").show()
        else:
          #  new_patient = Patient(id.get_text(), name.get_text(), last_name.get_text(), age.get_text(), sex.get_active_text(), self.pathf1_text, self.pathf2_text)
          #  model.create_patient(new_patient)
        #    self.current_patient = new_patient
            self.new_patient_data.hide()
            self.update_list()
            controller.exportSerieToPng(self.pathf2_text)
            self.series_image = builder.get_object("show-images")
            self.dcm_images_selected = 0
            self.show_images_study()
            self.new_patient_data.hide()
            self.series_image.show()

    def check_patient_data_window_confirm(self, button):
        builder.get_object("check-data-patient").hide()



    def added_new_patient_window(self,button):
        self.choose_action_window.hide()
        self.patients_list_window.show()
    
    def hide_dialog_confirm(self, button):
        self.patient_added_confirmation.hide()


    def tagt_details_button(self,button):
        window = builder.get_object("tagt-details-window")
        window.set_title("Selección de opciones de medida")
        self.choose_action_window.hide() 
        builder.get_object("tagtd-text").set_text("Seleccione las opciones TA-GT deseadas")   
        self.half_selected = builder.get_object("tagtd-options").get_active_text()
        self.measure_selected = "tagt"
        window.show()

    def br_details_button(self,button):
        window = builder.get_object("tagt-details-window")
        self.choose_action_window.hide()
        builder.get_object("tagtd-text").set_text("Seleccione las opciones Básica Rotuliana deseadas")       
        self.half_selected = builder.get_object("tagtd-options").get_active_text()
        self.measure_selected = "br"
        window.show()

    def do_other_measurements_button(self,button):
        self.measurements_details_window.hide()
        self.measurements_details_window = None
        self.choose_action_window.show()

    def store_bd_button(self,button):
        print("funciona")
        
    def print_lines_br_window_button(self,button):
        self.print_lines_br_window.show()


    


    def delete_patient(self, button):
        selection = builder.get_object("tree-list").get_selection()
        selection.set_mode(Gtk.SelectionMode.BROWSE)
        (model,paths) = selection.get_selected_rows()
        if len(paths)==1:
            for path in paths:
                tree_iter = model.get_iter(path)
                self.rowselected = model.get_value(tree_iter,0)
        confirm_delete = builder.get_object("confirm_delete_window")
        confirm_delete.set_title("Confirmar eliminación")
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

    def confirm_refine_lines_button(self, button):
        cv2.destroyAllWindows()
        print(self.line1[0][0], self.line2[0], self.line3)
        femur_left = self.line1[0][0]
        femur_right = self.line1[0][1]
        builder.get_object("print-lines-window").hide()
        builder.get_object("print-lines-window").hide()
        d = controller.refine_ta_gt(self.current_patient.femurRotulaImage.ds, (femur_left, femur_right), self.line2, self.line3)
        builder.get_object("patient-details-window").hide()
        builder.get_object("pd-tagtrl").set_text(str(d))
        builder.get_object("patient-details-window").show()
        print(d)


    def show_images_study(self):
        label = builder.get_object("si-text")
        if self.dcm_images_selected == 0:
            label.set_text("Escoja la imagen que muestre el fémur de manera óptima")
        if self.dcm_images_selected == 1:
            label.set_text("Escoja la imagen que muestre la tibia de manera óptima")
        filenames = os.listdir("temp")
        self.series_list = []
        for files in filenames:
            self.series_list.append("temp/" + files)
        self.series_list = sorted(self.series_list)
        self.series_iterator = 0
        img = builder.get_object("si-dcmimage")
        img.set_from_file(self.series_list[self.series_iterator])
        builder.get_object("show-images").show()
        builder.get_object("show-images").set_title("Estudio de imágenes")


    def selectDcmFile(self,button):
        if self.dcm_images_selected == 0:
            path_dcm = self.series_list[self.series_iterator]
            self.femurDcm = controller.pngPathToDCM(path_dcm,  self.pathf2_text)
            builder.get_object("si-text").set_text("Escoja la imagen que muestre la tibia de manera óptima")
            self.dcm_images_selected = 1
        elif self.dcm_images_selected == 1:
            path_dcm = self.series_list[self.series_iterator]
            self.tibiaDcm = controller.pngPathToDCM(path_dcm, self.pathf2_text)
            new_patient = Patient(self.id.get_text(), self.name.get_text(), self.last_name.get_text(), self.age, self.sex.get_active_text(), self.femurDcm, self.tibiaDcm)
            controller.create_patient(new_patient)
            self.current_patient = new_patient
            controller.removePngSeries()
            self.showPatientMenu()
            builder.get_object("show-images").hide()


    def cancelSelectDcmFile(self,button):
        if self.dcm_images_selected == 0:
            builder.get_object("show-images").hide()
            builder.get_object("new-patient").show()
        elif self.dcm_images_selected == 1:
            builder.get_object("si-text").set_text("Escoja la imagen que muestre el fémur de manera óptima") 
            self.femurDcm = ""
            self.dcm_images_selected = 0

    def showPatientMenu(self):
        window = builder.get_object("patient-details-window")
        window.set_title(self.current_patient.firstName + " " + self.current_patient.name)
        builder.get_object("pd-dni").set_text(self.current_patient.id)
        builder.get_object("pd-fstname").set_text(self.current_patient.firstName)
        builder.get_object("pd-name").set_text(self.current_patient.name)
        builder.get_object("pd-age").set_text(self.current_patient.age)
        builder.get_object("pd-sex").set_text(self.current_patient.sex)
        tagtr_l = controller.getStoredTAGTResult(self.current_patient, "Izquierda")
        if  tagtr_l != "":
            builder.get_object("pd-tagtrl").set_text(str(tagtr_l) + " mm")
        tagtr_r = controller.getStoredTAGTResult(self.current_patient, "Derecha")
        if  tagtr_r != "":
            builder.get_object("pd-tagtrr").set_text(str(tagtr_r)+ " mm")
        br_l = controller.getStoredBRResult(self.current_patient, "Izquierda")
        if  br_l != "":
            builder.get_object("pd-brl").set_text(str(br_l) + " º")
        br_r = controller.getStoredBRResult(self.current_patient, "Derecha")
        if  br_r != "":
            builder.get_object("pd-brr").set_text(str(br_r)+ " º")            
        img_femur = builder.get_object("pd-femur-image")
        img1 = controller.exportDStoPNG(self.current_patient.femurRotulaImage.originalImage)
        img2 = controller.exportDStoPNG(self.current_patient.tibiaImage.originalImage)
        img1 = cv2.resize(img1, (400,400))
        img2 = cv2.resize(img2, (400,400))
        im_v = cv2.vconcat([img1, img2])
        cv2.imwrite("femur.png", im_v)

        img_femur.set_from_file("femur.png")
        window.show()
        os.remove("femur.png")

    def patient_details_button(self,button):
        selection = builder.get_object("tree-list").get_selection()
        selection.set_mode(Gtk.SelectionMode.BROWSE)
        (modelo, paths) = selection.get_selected_rows()
        if len(paths)==1:
            for path in paths:
                tree_iter = modelo.get_iter(path)
                self.rowselected = modelo.get_value(tree_iter,0)
        patient = controller.get_patient(self.rowselected)
        self.current_patient = patient
        self.showPatientMenu()



    def show_measures_menu(self,button):
        builder.get_object("measures-options").show()
        builder.get_object("measures-options").set_title("Escoja la medida")


    def hide_measures_menu(self,button):
        builder.get_object("measures-options").hide()

    def accept_measure_menu(self, button):
        self.measure_selected = builder.get_object("mo-measure").get_active_text()
        self.half_selected = builder.get_object("mo-half").get_active_text()
        self.show_measures_window()

    def show_measures_window(self):
        d, img,lines = controller.getMeasures(self.measure_selected, self.half_selected, self.current_patient)
        self.measure_result = d
        builder.get_object("patient-details-window").hide()
        image_window = builder.get_object("tagt-img")
        text_window = builder.get_object("tagtr-text")
        builder.get_object("tagtr-dni").set_text(self.current_patient.id)
        builder.get_object("tagtr-fstname").set_text(self.current_patient.firstName)
        builder.get_object("tagtr-name").set_text(self.current_patient.name)
        builder.get_object("tagtr-age").set_text(self.current_patient.age)
        builder.get_object("tagtr-sex").set_text(self.current_patient.sex)
        builder.get_object("tagt-result").set_title("Resultados de la medida")

        
        cv2.imwrite("result.png", img)
        image_window.set_from_file("result.png")
        if self.measure_selected == "TA-GT":
            text_window.set_text("Resultado: " + str(d) + " mm")
        else:
            text_window.set_text("Resultado: " + str(d) + " º")

        builder.get_object("measures-options").hide()
        builder.get_object("tagt-result").show()
        self.interesting_points = lines

    def show_previous_image(self, button):
        if self.series_iterator == 0:
            self.series_iterator = len(self.series_list) -1
        else :
            self.series_iterator = self.series_iterator -1
        img = builder.get_object("si-dcmimage")

        img.set_from_file(self.series_list[self.series_iterator])
        
        
        
    def show_next_image(self, button):
        if self.series_iterator == len(self.series_list) -1:
            self.series_iterator = 0
        else :
            self.series_iterator = self.series_iterator + 1
        img = builder.get_object("si-dcmimage")
        img.set_from_file(self.series_list[self.series_iterator])

    def get_nearest_point(self, x, y):
        min_distance = -1
        candidate_points = None
        point_selected = None
        for points in self.interesting_points:
            d1 = math.sqrt( ((x - points[0][0]) **2)  + ((y - points[0][1]) **2))
            d2 = math.sqrt( ((x - points[1][0]) **2)  + ((y - points[1][1]) **2))
            if min_distance == -1:
                if d1 < d2:
                    min_distance = d1
                    point_selected = points[0]
                elif d2 < d1: 
                    min_distance = d2
                    point_selected = points[1]
                candidate_points = points
            elif min_distance > d1:
                min_distance = d1
                point_selected = points[0]
                candidate_points = points
            elif min_distance > d2:
                min_distance = d2
                candidate_points = points
                point_selected = points[1]


            
        return candidate_points, point_selected
    
    def print_lines_left_click(self, img):
        for points in self.interesting_points:
            cv2.circle(img, (points[0][0], points[0][1]), radius = 0, color = (255, 0, 0) , thickness = 3)
            cv2.circle(img, (points[1][0], points[1][1]), radius = 0, color = (255, 0, 0) , thickness = 3)
            cv2.line(img, points[0], points[1], color = (255, 0, 0), thickness = 1) 
        return img

    def print_lines_selection(self, img, x, y):
        nearest_points, point_selected = self.get_nearest_point(x, y)
        self.nearest_points = nearest_points
        self.point_selected = point_selected
        for points in self.interesting_points:
            if nearest_points[0] == points[0] and nearest_points[1] == points[1]:
                cv2.circle(img, (points[0][0], points[0][1]), radius = 0, color = (0, 255, 0) , thickness = 3)
                cv2.circle(img, (points[1][0], points[1][1]), radius = 0, color = (0, 255, 0) , thickness = 3)
                cv2.line(img, points[0], points[1], color = (0, 255, 0), thickness = 1)
                cv2.circle(img, (point_selected[0], point_selected[1]), radius = 0, color = (0, 0, 255) , thickness = 3)
            else:
                cv2.circle(img, (points[0][0], points[0][1]), radius = 0, color = (255, 0, 0) , thickness = 3)
                cv2.circle(img, (points[1][0], points[1][1]), radius = 0, color = (255, 0, 0) , thickness = 3)
                cv2.line(img, points[0], points[1], color = (255, 0, 0), thickness = 1) 
        return img

    def move_point(self, x,y,):
        for points in self.interesting_points:
            if points[0] == self.point_selected:
                points[0] = (x, y)
            elif points[1] == self.point_selected:
                points[1] = (x, y)

    def motion_notify(self, widget, event):
        x = int (event.x)
        y = int (event.y)
        img = builder.get_object("rf-img")
        img2 = cv2.imread('refine.png')
        h =  (int) (img2.shape[0] * 1.5)
        w = (int) (img2.shape[1] * 1.5)
      #  img2 = cv2.resize(img2, (h,w))
        if self.is_line_selected == True and event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.is_line_selected = not  (self.is_line_selected)
            img2 = self.print_lines_selection(img2, x, y)
        elif self.is_line_selected == False and event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.is_line_selected = not  (self.is_line_selected)
            img2 = self.print_lines_left_click(img2)
        elif  event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.move_point(x, y)
            img2 = self.print_lines_selection(img2, x, y)
        else: 
            img2 = self.print_lines_left_click(img2)
        cv2.imwrite('refine2.png', img2)
        img.set_from_file('refine2.png')

    def change_resolution(self,img, coefficient):
        img2 = cv2.imread('refine2.png')
        h =  (int) (self.current_size[0] * coefficient/self.current_zoom)
        w = (int) (self.current_size[1] * coefficient/self.current_zoom)
        self.current_size = (h,w)
        print(img.shape)
        print(h,w)
        img = cv2.resize(img, (h,w))
        lines = []
        for points in self.interesting_points:
            x1 = (int) (points[0][0] * coefficient/self.current_zoom)
            y1 = (int) (points [0][1] * coefficient/self.current_zoom)
            x2 = (int) (points[1][0] * coefficient/self.current_zoom)
            y2 = (int) (points[1][1] * coefficient/self.current_zoom)
            lines.append([(x1,y1), (x2,y2)])
        return lines, img



    def zoom_changed(self, combo):
        img = cv2.imread('refine.png')
        text = builder.get_object("rm-zoom").get_active_text()
        if text == "x1.5":
            if self.current_zoom != 1.5:
                lines, img = self.change_resolution(img, 1.5)
                cv2.imwrite('refine.png', img)
                self.interesting_points = lines
                img = self.print_lines_left_click(img)
                print(self.interesting_points)
                cv2.imwrite('refine2.png', img)
                img_window = builder.get_object("rf-img")
                img_window.set_from_file('refine2.png')
                self.current_zoom = 1.5
        elif text == "x1.75":
            if self.current_zoom != 1.75:
                lines, img = self.change_resolution(img, 1.75)
                cv2.imwrite('refine.png', img)
                self.interesting_points = lines
                img = self.print_lines_left_click(img)
                cv2.imwrite('refine2.png', img)
                img_window = builder.get_object("rf-img")
                img_window.set_from_file('refine2.png')
                self.current_zoom = 1.75
        elif text == "x1":
            if self.current_zoom != 1:
                lines, img = self.change_resolution(img, 1)
                cv2.imwrite('refine.png', img)
                self.interesting_points = lines
                img = self.print_lines_left_click(img)
                cv2.imwrite('refine2.png', img)
                img_window = builder.get_object("rf-img")
                img_window.set_from_file('refine2.png')
                self.current_zoom = 1
    


    def refine_measures(self, button):
        window = builder.get_object("refine-measure")
        img_window = builder.get_object("rf-img")
        if self.measure_selected == "TA-GT":
            img = controller.exportDStoPNG(self.current_patient.femurRotulaImage.originalImage + self.current_patient.tibiaImage.originalImage)
        elif self.measure_selected == "Básica Rotuliana":
            img = controller.exportDStoPNG(self.current_patient.femurRotulaImage.originalImage)
        cv2.imwrite("refine.png", img)
        img = self.print_lines_left_click(img)
        cv2.imwrite("refine2.png", img)

        img_window.set_from_file('refine2.png')
        eventbox = builder.get_object('rm-event')
        eventbox.connect("button-press-event", self.motion_notify)
        self.current_zoom = 1
        self.current_size = img.shape
        self.line_selected = None
        self.point_selected = None
        self.is_line_selected = False
        window.show()

    def confirm_refine(self,button):
        img = cv2.imread("refine.png")
        lines , _ = self.change_resolution(img, 1)
        self.interesting_points = lines
        d, img = controller.refineMeasure(self.measure_selected, self.interesting_points, self.current_patient)
        self.measure_result = d
        builder.get_object("refine-measure").hide()
        image_window = builder.get_object("tagt-img")
        text_window = builder.get_object("tagtr-text")
        cv2.imwrite("result.png", img)
        image_window.set_from_file("result.png")
        text_window.set_text(str(d))
        os.remove("refine.png")
        os.remove("refine2.png")
        builder.get_object("measures-options").hide()
        builder.get_object("tagt-result").show()

    def storeResult(self,button):
        os.remove("result.png")
        if self.measure_selected == "TA-GT":
            controller.storeTAGTResult(self.current_patient, self.measure_result, self.half_selected)
        else:
            controller.storeBRResult(self.current_patient, self.measure_result, self.half_selected)
        builder.get_object("tagt-result").hide()
        self.showPatientMenu()
        
    def fromPatientDetailsToList(self,button):
        builder.get_object("patient-details-window").hide()

    





bienvenida = builder.get_object("home-page")
bienvenida.set_title("Sistema de cálculo automático DICOM")
bienvenida.connect("delete-event", Gtk.main_quit)
builder.connect_signals(View())
bienvenida.show_all()
Gtk.main()