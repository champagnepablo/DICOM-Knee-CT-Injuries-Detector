import unittest
import sys
sys.path.insert(1,'../')
sys.path.append('../src')
sys.path.append('../../image-preprocessing/src')
from src import controller, model
from src import export_serie_to_png
from model import Patient


class TestController(unittest.TestCase):


    def testInsert(self):
        patient = Patient("1", "Name", "Last Name", "10/01/2001", "Hombre", "test.dcm", "test.dcm")
        controller.create_patient(patient)
        patient2 = controller.get_patient("1")
        id = controller.findPatient("1")
        self.assertEqual("1", patient2.id)
        self.assertEqual("1", id)


        isChanged = controller.storeTAGTResult(patient, 10, "Izquierda")
        self.assertEqual(True, isChanged)

        tagt = controller.getStoredTAGTResult(patient, "Izquierda")
        tagt2 = controller.getStoredTAGTResult(patient, "Derecha")
        self.assertEqual(10, tagt)
        self.assertEqual("", tagt2)
        controller.removePatient("1")

    def check



if __name__ == '__main__':
    unittest.main()
