# coding: utf-8
import os
import json
import tempfile
import time
from fractions import Fraction
import shutil

import tornado.ioloop
import tornado.web
import Adafruit_BMP.BMP085 as BMP085
import picamera

from config import PHOTO_STORE


class SensorAccess(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write(json.dumps(self.read_sensor()))
        self.finish()

    def read_sensor(self):
        raise NotImplementedError('Should be implemented in subclass')


class TempSensorAccess(SensorAccess):
    def read_sensor(self):
        sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
        return {
            'temperature': sensor.read_temperature(),
            'pressure': sensor.read_pressure(),
        }


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write(json.dumps({
            'index': 'pitools service'
        }))
        self.finish()


class CameraHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        resolution = (800, 450, )
        annotate_text = time.strftime(
            '%Y/%m/%d %H:%M:%S offset +{:d}s\n{:.2f}deg / {:.3f}KPa'
        )
        wait_offset = 1
        photo_dir = os.path.join(
            PHOTO_STORE,
            time.strftime('%Y%m%d')
        )
        not os.path.isdir(photo_dir) and os.makedirs(photo_dir, mode=777)
        with picamera.PiCamera() as camera:
            sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

            camera.annotate_text_size = 64
            camera.framerate = Fraction(15, 1)
            camera.awb_mode = 'fluorescent'
            camera.iso = 600
            fd, photo_path = tempfile.mkstemp(suffix='.jpg', prefix='pi')
            print fd, photo_path
            os.close(fd)
            photo_path = os.path.join(
                '/dev/shm',
                os.path.basename(photo_path)
            )
            # wait a moment for iso and white balance
            time.sleep(wait_offset)
            # and my camera is up side down, so rotate 180 deg
            camera.rotation = 180
            annotate_text = annotate_text.format(
                wait_offset,
                sensor.read_temperature(),
                sensor.read_pressure() / 1000.0
            )
            camera.annotate_text = annotate_text
            camera.capture(photo_path, resize=resolution)
            dst_photo_path = os.path.join(
                photo_dir,
                '{}.jpg'.format(str(int(time.time())))
            )
            shutil.move(photo_path, dst_photo_path)


def start_server():
    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/sensors/env", TempSensorAccess),
    ])
    application.listen(9876)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start_server()
