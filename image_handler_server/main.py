import os

from flask import Flask, request, secure_filename
from PIL import Image

app = Flask(__name__)
SAVE_DIR = '/home/aurora/motion_detected'
if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)


@app.post('/')
def index():
    print("Request received")
    image_one = request.files['image_one']
    if not image_one:
        print('No image')
        return str(0)
    image_two = request.files['image_two']

    return calculate_image_difference(image_one, image_two)  # you can customize index.html here


def calculate_image_difference(image_one, image_two):
    print("Calculating difference")
    i1 = Image.open(image_one)
    i2 = Image.open(image_two)

    current_hist = i1.histogram()
    previous_hist = i2.histogram()

    hist_diff = sum([abs(c - p) for c, p in zip(current_hist, previous_hist)]) / len(current_hist)
    print(f"Difference: {hist_diff}")
    if hist_diff >= 100:
        save_files(image_one, i1, i2)
    return str(hist_diff)


def save_files(filestorage_image, image_one, image_two):
    original_file_name = secure_filename(filestorage_image.filename)
    image_time = original_file_name.replace('motion_detected_', '').replace('.png', '')
    image_dir = os.path.join(SAVE_DIR, image_time)
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)
    file_one = (os.path.join(image_dir, 'image_one.png'), image_one)
    file_two = (os.path.join(image_dir, 'image_two.png'), image_two)
    for f in (file_one, file_two):
        f[1].save(f[0])


def main():
    app.run(host='0.0.0.0', debug=False)


if __name__ == "__main__":
    main()
