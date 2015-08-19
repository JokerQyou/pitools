# coding: utf-8
import json

import tornado.ioloop
import tornado.web
import Adafruit_BMP.BMP085 as BMP085


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


def start_server():
    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/sensors/env", TempSensorAccess),
    ])
    application.listen(9876)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start_server()
