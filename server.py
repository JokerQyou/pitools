# coding: utf-8
import os
import json
import tempfile
import time
from fractions import Fraction
import random
import shutil

import tornado.ioloop
import tornado.web
import Adafruit_BMP.BMP085 as BMP085
import picamera

from config import PHOTO_STORE, PHOTO_RESOLUTION, NORMAL_USER

LAST_DAILY_SHOT = 0
TODAY = '0'

sensor = None
camera = None


def get_last_daily_shot_id():
    photo_dir = get_daily_shot_dir()
    p_id = -1
    for item in os.listdir(photo_dir):
        try:
            _p_id = int(os.path.splitext(item)[0])
        except Exception:
            continue
        if _p_id > p_id:
            p_id = _p_id
    return p_id


def get_daily_shot_dir():
    global TODAY
    dirname = time.strftime('%Y%m%d')
    if dirname != TODAY:
        generate_daily_video(
            os.path.join(PHOTO_STORE, TODAY)
        )
        TODAY = dirname
    photo_dir = os.path.join(
        PHOTO_STORE,
        dirname
    )
    not os.path.isdir(photo_dir) and os.makedirs(photo_dir, mode=0777)
    return photo_dir


def generate_daily_video(path):
    command = 'avconv -f image2 -framerate 10 -i %04d.jpg -codec copy {}.mkv'
    cur_dir = os.path.abspath(os.curdir)
    try:
        os.chdir(path)
        os.system(
            command.format(os.path.basename(path))
        )
    except Exception as e:
        print e
    finally:
        os.chdir(cur_dir)


def format_to_file_name(id, ext='jpg', digits=4):
    ext = ext if not ext.startswith('.') else ext[1:]
    str_id = str(id)
    n = digits - len(str_id)
    str_id = '0' * n + str_id if n > 0 else str_id
    return '.'.join([str_id, ext, ])


class SensorAccess(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write(json.dumps(self.read_sensor()))
        self.finish()

    def read_sensor(self):
        raise NotImplementedError('Should be implemented in subclass')


class TempSensorAccess(SensorAccess):
    def read_sensor(self):
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
        self.write(self.take_photo(self.generate_path()))
        self.finish()

    def generate_path(self, daily=False):
        photo_dir = get_daily_shot_dir()
        if not daily:
            photo_dir = os.path.join(
                photo_dir,
                'random'
            )
        if not os.path.isdir(photo_dir):
            normal_user = shutil.getpwnam(NORMAL_USER)
            os.makedirs(photo_dir, mode=0777)
            os.chown(photo_dir, normal_user.pw_uid, normal_user.pw_gid)
        if daily:
            dst_photo_path = os.path.join(
                photo_dir,
                format_to_file_name(get_last_daily_shot_id() + 1)
            )
        else:
            dst_photo_path = os.path.join(
                photo_dir,
                format_to_file_name(
                    '{:d}{:f}'.format(
                        get_last_daily_shot_id() + 1,
                        random.random()
                    )
                )
            )
        return dst_photo_path

    def take_photo(self, path, daily=False):
        annotate_text = time.strftime(
            '%Y/%m/%d %H:%M:%S offset +{:d}s  {:.2f}deg / {:.3f}KPa'
        )
        wait_offset = 1
        now = time.time()
        global LAST_DAILY_SHOT
        if daily and now - LAST_DAILY_SHOT < 50:
            print LAST_DAILY_SHOT, now, daily
            return ''
        photo_path = tempfile.mktemp(suffix='.jpg', prefix='pi')
        photo_path = os.path.join(
            '/dev/shm',
            os.path.basename(photo_path)
        )
        annotate_text = annotate_text.format(
            wait_offset,
            sensor.read_temperature(),
            sensor.read_pressure() / 1000.0
        )
        camera.annotate_text = annotate_text
        camera.capture(photo_path, resize=PHOTO_RESOLUTION)
        shutil.move(photo_path, path)
        normal_user = shutil.getpwnam(NORMAL_USER)
        os.chown(path, normal_user.pw_uid, normal_user.pw_gid)
        os.chmod(path, 0777)
        if daily:
            LAST_DAILY_SHOT = now
        return path


class DailyPhotoHandler(CameraHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write(
            self.take_photo(
                self.generate_path(daily=True),
                daily=True
            )
        )
        self.finish()


def start_server():
    global sensor, camera
    wait_offset = 1
    with picamera.PiCamera() as camera:
        sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

        camera.annotate_text_size = 50
        # camera.annotate_background = picamera.Color(r=204, g=204, b=204)
        camera.framerate = Fraction(15, 1)
        camera.awb_mode = 'fluorescent'
        camera.iso = 600
        # wait a moment for iso and white balance
        time.sleep(wait_offset)
        # and my camera is up side down, so rotate 180 deg
        camera.rotation = 180

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
