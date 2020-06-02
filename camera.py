
import cv2
import numpy as np

class Camera(object):
    def get_img(self):
        raise NotImplementedError()
        
class OpenCVCamera(Camera):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1);

    def get_img(self):
        ret,frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame, 3)
        return frame