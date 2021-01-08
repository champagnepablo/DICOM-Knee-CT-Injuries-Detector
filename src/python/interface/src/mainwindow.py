import sys
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
import pydicom
import sys
sys.path.append('../../image-preprocessing/src')
from image_utils import dicom_utils, image_processing, interesting_points
class MainWindow(QMainWindow):

    def convert_nparray_to_QPixmap(self,img):
        w,h = img.shape
        # Convert resulting image to pixmap
        if img.ndim == 1:
            img =  cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        qimg = QImage(img.data, h, w, 3*h, QImage.Format_RGB888) 
        qpixmap = QPixmap(qimg)

        return qpixmap

    def __init__(self):
        super(MainWindow, self).__init__()
        self.title = "Image Viewer"
        self.setWindowTitle(self.title)

        label = QLabel(self)
        ds=pydicom.dcmread('/home/pablo/Documentos/TFG/src/python/image-preprocessing/data/dicom/tibia.dcm')
        img_hu = dicom_utils.transformToHu(ds,ds.pixel_array)
        normalized_img = dicom_utils.normalizeImage255(img_hu, ds.WindowCenter[0], ds.WindowWidth[0])
        pixmap = self.convert_nparray_to_QPixmap(normalized_img)
        label.setPixmap(pixmap)
        self.setCentralWidget(label)
        self.resize(pixmap.width(), pixmap.height())


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())