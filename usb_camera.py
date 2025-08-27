import cv2 as cv
import time
from datetime import datetime
import numpy as np


class UsbVideoCamera(object):
    def __init__(self, flip=False, file_type=".jpg", photo_string="stream_photo"):
        self.vs = cv.VideoCapture(0)
        self.flip = flip  # Flip frame vertically
        self.file_type = file_type  # image type i.e. .jpg
        self.photo_string = photo_string  # Name to save the photo
        time.sleep(2.0)

    def __del__(self):
        self.vs.release()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        ret, frame = self.vs.read()
        return frame

    def get_frame_bytes(self):
        ret, jpeg = cv.imencode(self.file_type, self.get_frame())
        return jpeg.tobytes()

    # Take a photo, called by camera button
    def take_picture(self):
        frame = self.flip_if_needed(self.get_frame())
        today_date = datetime.now().strftime("%m%d%Y-%H%M%S")  # get current time
        photo_name = str(self.photo_string + "_" + today_date + self.file_type)
        cv.imwrite(photo_name, frame)
        return photo_name
