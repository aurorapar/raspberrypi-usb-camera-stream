from datetime import datetime
from queue import Queue
from threading import Thread
import time

import cv2 as cv
import numpy as np

from image_handler import calculate_frame_difference, calculate_frame_difference_network


class UsbVideoCamera(object):
    def __init__(self, flip=False, file_type=".jpg", photo_string="motion_detected", wait_time=5, destination_server=None):
        self.flip = flip  # Flip frame vertically
        self.file_type = file_type  # image type i.e. .jpg
        self.photo_string = photo_string  # Name to save the photo
        self.wait_time = wait_time
        self.destination_server = destination_server
        self.frame_queue = Queue()
        self.detecting_motion = False
        self.camera_stream = cv.VideoCapture(0, cv.CAP_V4L2)

        self.gather_frames_thread = Thread(target=self.gather_frames_loop)
        self.motion_detection_thread = Thread(target=self.detect_motion_over_network_loop)
        self.network_queue_thread = Thread(target=self.process_network_queue_loop)
        self.network_queue = Queue()

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
            frame_one = self.get_frame()
            frame_two = self.get_frame()
            self.frame_queue.put((frame_one, frame_two))
            time.sleep(self.wait_time)

    def stop_motion_detection(self):
        if self.detecting_motion:
            self.detecting_motion = False
            self.motion_detection_thread.join()
            print("Motion detection halted")

    def detect_motion_loop(self):
        print(f"Started detecting motion at {time.ctime()}\n\n")
        while True:
            if not self.detecting_motion:
                break
            time.sleep(self.wait_time)
            self.detect_motion()

    def detect_motion(self):
        print("Trying to detect motion")
        frames = self.frame_queue.get()
        difference = calculate_frame_difference(frames[0], frames[1])
        self.frame_queue.task_done()
        print(f"Difference: {difference}")
        return difference

    def detect_motion_over_network_loop(self):
        print(f"Started detecting motion at {time.ctime()}\n\n")
        self.network_queue_thread.start()
        while True:
            if not self.detecting_motion:
                break
            time.sleep(self.wait_time)
            self.detect_motion_over_network()

    def detect_motion_over_network(self):
        frames = self.frame_queue.get()
        pic_one = self.save_frame(frames[0])
        pic_two = self.save_frame(frames[1])
        data = (pic_one, pic_two)
        self.frame_queue.task_done()
        network_thread = Thread(target=calculate_frame_difference_network, args=(data, self.destination_server))
        self.network_queue.put(network_thread)
        network_thread.start()

    def process_network_queue_loop(self):
        while True:
            if not self.detecting_motion:
                break
            time.sleep(max(.01, self.wait_time / 3))
            if self.network_queue.empty():
                continue
            network_thread = self.network_queue.get()
            network_thread.join()
            self.network_queue.task_done()
