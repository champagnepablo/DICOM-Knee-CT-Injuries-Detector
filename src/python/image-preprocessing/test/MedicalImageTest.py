import unittest
import sys
sys.path.insert(1,'../src')
from model.MedicalImage import MedicalImage
import pydicom
class MedicalImageTest(unittest.TestCase):



    def test_medical(self):
        ds = pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/tibia.dcm')
        med_img = MedicalImage('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/tibia.dcm')
        self.assertEqual(ds.PixelSpacing, med_img.getPixelSpacing())
        self.assertEqual(ds.RescaleSlope, med_img.getRescaleSlope())






if __name__ == '__main__':
    unittest.main()