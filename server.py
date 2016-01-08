# coding: utf-8
from __future__ import unicode_literals

from flask import Flask
import pitools

app = Flask(__name__)
app.register_blueprint(pitools.camera.blueprint)
app.register_blueprint(pitools.sensors.bmp085.blueprint, url_prefix='/sensors')


def serve():
    app.run('0.0.0.0', 9876)

if __name__ == '__main__':
    serve()
