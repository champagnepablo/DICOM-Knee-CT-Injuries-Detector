import json

def write_json(data, filename='data.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 


def create_patient(patient_id, first_name = None, last_name = None, age = None, sex = None):
    if (find_patient(patient_id) != None):
        return False
    else :
        with open('data.json') as json_file: 
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
                        'coordinates_trochlea':'',
                        'coordinates_condiles':'' ,
                        'coordinates_rotula': ''
                    },
                    'img_tibia': {
                        'file_tibia': '',
                        'coordinates_tibia': ''
                    },
                    'results': {
                        'rb': '',
                        'ta_gt': ''
                    }
                }
            temp.append(new_patient)
        write_json(data)
        return True

def find_patient(id):
    data = json.loads(open("data.json").read())
    patient = None
    for i in data['patients']:
        if i['patient_id'] == id:
            patient = i
    return patient

def remove_patient(id):
    with open('data.json') as data_file:
        data = json.load(data_file)
        for i in range(len(list(data['patients']))):
            if data['patients'][i]['patient_id'] == id:
                del data['patients'][i] 
    with open('data.json', 'w') as data_file:
        data = json.dump(data, data_file, indent=4)

def set_name(id, first_name, last_name):
    changed = False
    with open('data.json') as data_file:
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
    with open('data.json') as data_file:
        data = json.load(data_file)
        for i in data['patients']:
            if i['patient_id'] == id:
                changed = True
                i['age'] = age
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
create_patient(2, "Joaquín", "Valeiro Pena",19,"M")
find_patient(1)
#remove_patient(2)
#set_name(1,"Pedro", "Sanchez")