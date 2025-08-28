import sys
import os

from PIL import Image
import requests


def calculate_frame_difference(frame_one, frame_two):
    image_one = Image.fromarray(frame_one)
    image_two = Image.fromarray(frame_two)

    current_hist = image_one.histogram()
    previous_hist = image_two.histogram()

    hist_diff = sum([abs(c - p) for c, p in zip(current_hist, previous_hist)]) / len(current_hist)

    return hist_diff


def calculate_frame_difference_network(image_files):
    url = 'http://192.168.1.142:5001'
    with open(image_files[0], 'rb') as f1:
        with open(image_files[1], 'rb') as f2:
            payload = {
                'image_one': (image_files[0], f1.read())
                ,'image_two': (image_files[1], f2.read())
            }

            image_size = sys.getsizeof(payload) + sys.getsizeof(payload['image_one']) + sys.getsizeof(payload['image_two'])
            print(f"sending network request, payload size: {image_size}")
            headers = {'Content-Length': str(image_size)}
            try:
                requests.post(url, files=payload, headers=headers, stream=True, timeout=(.5, 1*10**-9))
            except requests.exceptions.ReadTimeout:
                pass
            print("network request handled")
    for f in image_files:
        os.remove(f)
