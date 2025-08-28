from PIL import Image
import requests


def calculate_frame_difference(frame_one, frame_two):
    image_one = Image.fromarray(frame_one)
    image_two = Image.fromarray(frame_two)

    current_hist = image_one.histogram()
    previous_hist = image_two.histogram()

    hist_diff = sum([abs(c - p) for c, p in zip(current_hist, previous_hist)]) / len(current_hist)

    return hist_diff


def calculate_frame_difference_network(frames):
    url = 'http://192.168.1.142:5000'
    payload = {
        'frame_one': frames[0].tolist()
        ,'frame_two': frames[1].tolist()
    }
    headers = {'Content-Type': 'application/json'}
    print("sending network request")
    requests.post(url, json=payload, headers=headers)
    print("network request handled")
