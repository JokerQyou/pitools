# coding: utf-8
from __future__ import unicode_literals

from flask import Flask
from pitools import camera

app = Flask(__name__)
app.register_blueprint(camera.blueprint)


def serve():
    app.run('0.0.0.0', 9876)

if __name__ == '__main__':
    serve()
