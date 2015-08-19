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

from config import PHOTO_STORE, PHOTO_RESOLUTION


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
        self.write(self.__take_photo(self.__generate_path()))
        self.finish()

    def __generate_path(self, daily=False):
        photo_dir = os.path.join(
            PHOTO_STORE,
            time.strftime('%Y%m%d')
        )
        if not daily:
            photo_dir = os.path.join(
                photo_dir,
                'random'
            )
        not os.path.isdir(photo_dir) and os.makedirs(photo_dir, mode=777)
        dst_photo_path = os.path.join(
            photo_dir,
            '{}.jpg'.format(str(int(time.time())))
        )
        return dst_photo_path

    def __take_photo(self, path):
        annotate_text = time.strftime(
            '%Y/%m/%d %H:%M:%S offset +{:d}s\n{:.2f}deg / {:.3f}KPa'
        )
        wait_offset = 1
        with picamera.PiCamera() as camera:
            sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

            camera.annotate_text_size = 64
            camera.framerate = Fraction(15, 1)
            camera.awb_mode = 'fluorescent'
            camera.iso = 600
            photo_path = tempfile.mktemp(suffix='.jpg', prefix='pi')
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
            camera.capture(photo_path, resize=PHOTO_RESOLUTION)
        shutil.move(photo_path, path)
        return path


class DailyPhotoHandler(CameraHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write(
            self.__take_photo(self.__generate_path(daily=True))
        )
        self.finish()


def start_server():
    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/sensors/env", TempSensorAccess),
        (r'/photo/shot', CameraHandler),
        (r'/photo/daily', DailyPhotoHandler),
    ])
    application.listen(9876)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start_server()
