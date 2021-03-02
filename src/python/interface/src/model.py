import json
import sys
sys.path.append('../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/model')
sys.path.insert(1, '../../image-preprocessing/src/')

from PatientHistorial import Patient
from MedicalImage import FemurRotulaImage, TibiaImage

DATA_PATH = 'data/data.json'

def write_json(data, filename=DATA_PATH): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 

def create_patient(patient ):
    if (True == False):
        return False
    else :
        with open(DATA_PATH) as json_file: 
            data = json.load(json_file) 
            temp = data['patients']
            new_patient = {
                    'patient_id' : patient.id,
                    'first_name' : patient.firstName,
                    'last_name'  : patient.name,
                    'date': '',
                    'age': patient.age,
                    'sex': patient.sex,
                    'img_femur': {
                        'file_femur': patient.femurRotulaImage.fileName
                    },
                    'img_tibia': {
                        'file_tibia': patient.tibiaImage.fileName,
                    },
                    'results': {
                        'rb_left': '',
                        'rb_right':'',
                        'ta_gt_left': '',
                        'ta_gt_right': ''
                    }
                }
            temp.append(new_patient)
        write_json(data)
        return True

def get_patients():
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        return data


def find_patient(id):
    data = json.loads(open(DATA_PATH).read())
    patient = None
    for i in data['patients']:
        if i['patient_id'] == id:
            patient = id
    return patient

def get_patient(id):
    data = json.loads(open(DATA_PATH).read())
    patient = None
    for i in data['patients']:
        if i['patient_id'] == id:
            patient_id = i['patient_id']
            age = i['age']
            fst_name = i['first_name']
            last_name = i['last_name']
            sex = i['sex']
            femurFile = i['img_femur']['file_femur']
            tibiaFile = i['img_tibia']['file_tibia']
            patient = Patient(patient_id, fst_name, last_name, age, sex, femurFile, tibiaFile)
    return patient


def get_tagt_result(id, half= "left"):
    data = json.loads(open(DATA_PATH).read())
    points = ""
    for i in data['patients']:
        if i['patient_id'] == id:
            if half == "left":
                points = i['results']['ta_gt_left']
            if half == "right":
                points = i['results']['ta_gt_right']
    return points 

def get_br_result(id, half= "left"):
    data = json.loads(open(DATA_PATH).read())
    points = ""
    for i in data['patients']:
        if i['patient_id'] == id:
            if half == "left":
                points = i['results']['rb_left']
            if half == "right":
                points = i['results']['rb_right']
    return points 

def remove_patient(id):
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        list_patients = list(data['patients'])
        for i in range(len(list(data['patients'])) ):
            if list_patients[i]['patient_id'] == id:
                print("removed")
                print(i)
                del data['patients'][i] 
    write_json(data)

def set_tagt_result(id, result, half = "left"):
    changed = False 
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                if half == "left":
                    i["results"]['ta_gt_left'] = result
                else:
                    i["results"]['ta_gt_right'] = result
            write_json(data)
    return changed

def set_br_result(id, result, half = "left"):
    changed = False 
    with open('data.json') as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                if half == "left":
                    i["results"]['rb_left'] = result
                else:
                    i["results"]['rb_right'] = result
            write_json(data)
    return changed


