

class Camera(object):
    def get_img(self):
        raise NotImplementedError()
        
class OpenCVCamera(Camera):
    def __init__(self):
        pass
    def get_img(self):
        pass