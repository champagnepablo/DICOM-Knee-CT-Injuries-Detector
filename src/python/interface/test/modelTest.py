import unittest
import sys
sys.path.insert(1,'../')
sys.path.append('../src')
sys.path.append('../../image-preprocessing/src')
from src import model
from src import export_serie_to_png
from model import Patient


class TestModel(unittest.TestCase):


    def test_insert(self):
        patient = Patient("1", "Name", "Last Name", "10/01/2001", "Hombre", "test.dcm", "test.dcm")
        model.create_patient(patient)
        patient2 = model.get_patient("1")
        id = model.find_patient("1")
        self.assertEqual("1", patient2.id)
        self.assertEqual("1", id)
        isChanged = model.set_tagt_result("1", 10, "left")
        self.assertEqual(True, isChanged)

        tagt = model.get_tagt_result("1", "left")
        tagt2 = model.get_tagt_result("1", "right")
        self.assertEqual(10, tagt)
        self.assertEqual("", tagt2)
        model.remove_patient("1")



if __name__ == '__main__':
    unittest.main()
