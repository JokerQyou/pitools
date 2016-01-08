# coding: utf-8
from __future__ import unicode_literals
import time

from flask import Blueprint, current_app, jsonify
import Adafruit_BMP.BMP085 as BMP085

blueprint = Blueprint('BMP085', __name__, url_prefix='/bmp085')
DEFAULT_RES = BMP085.BMP085_ULTRAHIGHRES


def setup_bmp085():
    '''
    Instantiate and return a BMP085 object
    '''
    bmp085 = BMP085.BMP085(mode=DEFAULT_RES)
    return bmp085


@blueprint.route('/all', methods=('GET', ))
def read_all():
    '''
    Read temperature and air pressure
    '''
    return jsonify(
        temperature=current_app.bmp085.read_temperature(),
        pressure=current_app.bmp085.read_pressure(),
        timestamp=time.time()
    )


@blueprint.route('/temperature', methods=('GET', ))
def read_temperature():
    '''
    Read temperature
    '''
    if not isinstance(getattr(current_app, 'bmp085', None), BMP085.BMP085):
        setattr(current_app, 'bmp085', setup_bmp085())
    return jsonify(
        temperature=current_app.bmp085.read_temperature(),
        timestamp=time.time()
    )


@blueprint.route('/pressure', methods=('GET', ))
def read_pressure():
    '''
    Read air pressure
    '''
    if not isinstance(getattr(current_app, 'bmp085', None), BMP085.BMP085):
        setattr(current_app, 'bmp085', setup_bmp085())
    return jsonify(
        pressure=current_app.bmp085.read_pressure(),
        timestamp=time.time()
    )

