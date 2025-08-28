from datetime import datetime
from queue import Queue
from threading import Thread

import cv2 as cv
import numpy as np

from image_handler import calculate_frame_difference, calculate_frame_difference_network


class UsbVideoCamera(object):
    def __init__(self, flip=False, file_type=".jpg", photo_string="motion_detected"):
        self.flip = flip  # Flip frame vertically
        self.file_type = file_type  # image type i.e. .jpg
        self.photo_string = photo_string  # Name to save the photo
        self.gather_frames_thread = Thread(target=self.gather_frames_loop)
        self.motion_detection_thread = Thread(target=self.detect_motion_loop)
        self.frame_queue = Queue()
        self.detecting_motion = False
        self.camera_stream = cv.VideoCapture(0)

    def __del__(self):
        self.camera_stream.release()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = None
        for x in range(5):
            ret, frame = self.camera_stream.read()
        return frame

    def get_frame_bytes(self):
        ret, jpeg = cv.imencode(self.file_type, self.get_frame())
        return jpeg.tobytes()

    # Take a photo, called by camera button
    def take_picture(self):
        frame = self.flip_if_needed(self.get_frame())
        return self.save_frame(frame)

    def save_frame(self, frame):
        today_date = datetime.now().strftime("%m%d%Y-%H%M%S%f")  # get current time
        photo_name = str(self.photo_string + "_" + today_date + self.file_type)
        cv.imwrite(photo_name, frame)
        return photo_name

    def start_motion_detection(self):
        self.detecting_motion = True
        self.gather_frames_thread.start()
        self.motion_detection_thread.start()

    def gather_frames_loop(self):
        while True:
            if not self.detecting_motion:
                break
            frames = (self.get_frame(), self.get_frame())
            self.frame_queue.put(frames)

    def stop_motion_detection(self):
        if self.detecting_motion:
            self.detecting_motion = False
            self.motion_detection_thread.join()
            print("Motion detection halted")

    def detect_motion_loop(self):
        while True:
            if not self.detecting_motion:
                break
            self.detect_motion_over_network()

    def detect_motion(self):
        print("Trying to detect motion")
        frames = self.frame_queue.get()
        difference = calculate_frame_difference(frames[0], frames[1])
        self.frame_queue.task_done()
        print(f"Difference: {difference}")
        return difference

    def detect_motion_over_network(self):
        print("Trying to detect motion")
        frames = self.frame_queue.get()
        pic_one = self.save_frame(frames[0])
        pic_two = self.save_frame(frames[1])
        data = (pic_one, pic_two)
        self.frame_queue.task_done()
        arg = (frames[0], frames[1])
        network_thread = Thread(target=calculate_frame_difference_network, args=(data,))
        network_thread.start()





