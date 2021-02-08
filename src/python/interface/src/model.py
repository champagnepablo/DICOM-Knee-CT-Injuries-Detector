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


def create_patient(patient_id, first_name = None, last_name = None, age = None, sex = None):
    if (find_patient(patient_id) != None):
        return False
    else :
        with open(DATA_PATH) as json_file: 
            data = json.load(json_file) 
            temp = data['patients']
            if (first_name == None):
                first_name = ''
            if (last_name == None):
                last_name = ''
            if (age == None):
                age = 'Unknown'
            if (sex == None or (sex != 'M' and sex != 'F')):
                sex = 'Unknown'
            new_patient = {
                    'patient_id' : patient_id,
                    'first_name' : first_name,
                    'last_name'  : last_name,
                    'age': age,
                    'sex': sex,
                    'img_femur': {
                        'file_femur': '',
                        'coordinates_trochlea_left':'',
                        'coordinates_trochlea_right':'',
                        'coordinates_condiles_left': {
                            'left': '',
                            'right': ''
                        },
                        'coordinates_condiles_right': {
                            'left': '',
                            'right': ''
                        },
                        'coordinates_rotula': ''
                    },
                    'img_tibia': {
                        'file_tibia': '',
                        'coordinates_tibia_left': '',
                        'coordinates_tibia_right': ''
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
                    'age': patient.age,
                    'sex': patient.sex,
                    'img_femur': {
                        'file_femur': patient.femurRotulaImage.fileName,
                        'coordinates_trochlea_left':'',
                        'coordinates_trochlea_right':'',
                        'coordinates_condiles_left': {
                            'left': '',
                            'right': ''
                        },
                        'coordinates_condiles_right': {
                            'left': '',
                            'right': ''
                        },
                        'coordinates_rotula_left': {
                            "left":'',
                            "right":''
                        },
                         'coordinates_rotula_right': {
                             "left":"",
                             "right":""
                         }   
                    },
                    'img_tibia': {
                        'file_tibia': patient.tibiaImage.fileName,
                        'coordinates_tibia_left': '',
                        'coordinates_tibia_right': ''
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

def get_trochlea_points(id, half = "left"):
    data = json.loads(open(DATA_PATH).read())
    points = None
    for i in data['patients']:
        if i['patient_id'] == id:
            if half == "left":
                points = i['img_femur']['coordinate_trochlea_left']
            if half == "right":
                points = i['img_femur']['coordinate_trochlea_right']
            
    return points

def get_condiles_points(id, half = "left"):
    data = json.loads(open(DATA_PATH).read())
    points_left = None
    points_right = None
    for i in data['patients']:
        if i['patient_id'] == id:
            if half == "left":
                points_left = i['img_femur']['coordinate_condiles_left']['left']
                points_right = i['img_femur']['coordinate_condiles_left']['right']
            if half == "right":
                points_left = i['img_femur']['coordinate_condiles_right']['left']
                points_right = i['img_femur']['coordinate_condiles_right']['right']
            
    return points_left, points_right

def get_rotula_points(id, half = "left"):
    data = json.loads(open(DATA_PATH).read())
    points_left = None
    points_right = None
    for i in data['patients']:
        if i['patient_id'] == id:
            if half == "left":
                points_left = i['img_femur']['coordinate_rotula_left']['left']
                points_right = i['img_femur']['coordinate_rotula_left']['right']
            if half == "right":
                points_left = i['img_femur']['coordinate_rotula_right']['left']
                points_right = i['img_femur']['coordinate_rotula_right']['right']
            
    return points_left, points_right   

def get_tibia_points(id, half = "left"):
    data = json.loads(open(DATA_PATH).read())
    points = None
    for i in data['patients']:
        if i['patient_id'] == id:
            if half == "left":
                points = i['img_tibia']['coordinate_tibia_left']
            if half == "right":
                points = i['img_tibia']['coordinate_tibia_right']
    return points

def get_tagt_result(id, half= "left"):
    data = json.loads(open(DATA_PATH).read())
    for i in data['patients']:
        if i['patient_id'] == id:
            if half == "left":
                points = i['results']['ta_gt_left']
            if half == "right":
                points = i['results']['ta_gt_right']
    return points 

def get_br_result(id, half= "left"):
    data = json.loads(open(DATA_PATH).read())
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
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)

def set_name(id, first_name, last_name):
    changed = False
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                i['first_name'] = first_name
                i['last_name'] = last_name
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)
    return changed

def set_age(id, age):
    changed = False 
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                i['age'] = age
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)
    return changed 

def set_points_trochlea(id, points, half = "left"):
    changed = False 
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                if half == "left":
                    i["img_femur"]['coordinates_trochlea_left'] = points
                else:
                    i["img_femur"]['coordinates_trochlea_right'] = points
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)
    return changed 

def set_points_tibia(id, points, half = "left"):
    changed = False 
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                if half == "left":
                    i["img_tibia"]['coordinates_tibia_left'] = points
                else:
                    i["img_femur"]['coordinates_tibia_right'] = points
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)
    return changed 

def set_points_condiles(id, points_left, points_right, half = "left"):
    changed = False 
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                if half == "left":
                    i["img_femur"]['coordinates_condiles_left']['left'] = points_left
                    i["img_femur"]['coordinates_condiles_left']['right'] = points_right
                else:
                    i["img_femur"]['coordinates_condiles_right']['left'] = points_left
                    i["img_femur"]['coordinates_condiles_right']['right'] = points_right
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)
    return changed 

def set_points_rotula(id, points_left, points_right, half = "left"):
    changed = False 
    with open(DATA_PATH) as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                if half == "left":
                    i["img_femur"]['coordinates_rotula_left']['left'] = points_left
                    i["img_femur"]['coordinates_rotula_left']['right'] = points_right
                else:
                    i["img_femur"]['coordinates_rotula_right']['left'] = points_left
                    i["img_femur"]['coordinates_rotula_right']['right'] = points_right
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)
    return changed 

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
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)
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
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)
    return changed 

def set_sex(id, sex):
    with open('data.json') as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                i['sex'] = sex
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)




#create_patient(1, "Pablo", "Valeiro Pena",24,"M")
#create_patient(2, "Joaquín", "Valeiro Pena",19,"M")
#find_patient(1)
#patient = Patient("56212345T","Maria", "Martinez", "30", "M", "/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/prueba.dcm", "/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/prueba.dcm" )
#create_patient(patient)
#remove_patient(10)
#set_name(1,"Pedro", "Sanchez")