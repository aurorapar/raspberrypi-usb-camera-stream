import argparse
import signal

from flask import Flask, render_template, Response

from usb_camera import UsbVideoCamera

pi_camera = None
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')  # you can customize index.html here


def gen(camera):
    # get camera frame
    while True:
        frame_bytes = camera.get_frame_bytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# Take a photo when pressing camera button
@app.route('/picture')
def take_picture():
    photo_name = pi_camera.take_picture()
    return photo_name


def signal_handler(signal_handle, frame):
    print("\nStopping program...")
    pi_camera.stop_motion_detection()
    print("Motion detection halted")
    exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Pi Camera Stream',
        description='Create your own live stream from a Raspberry Pi using the Pi camera module or a USB web cam.'
    )
    parser.add_argument('-c', '--camera-type', help="Camera type to use", default='usb', choices=['usb'])
    parser.add_argument('-f', '--flip', help="Flips pictures taken vertically", type=bool, default=False)
    parser.add_argument('-t', '--file-type', help="Format for pictures taken", default='.jpeg')

    args = parser.parse_args()
    camera_objects = {
        # 'module': ModuleVideoCamera,
        'usb': UsbVideoCamera
    }

    print("Arguments handled")
    pi_camera = camera_objects[args.camera_type](flip=args.flip, file_type=args.file_type)
    pi_camera.start_motion_detection()

    signal.signal(signal.SIGINT, signal_handler)
    app.run(host='0.0.0.0', debug=False)

