# coding: utf-8
'''
Test pitools.sensors.bmp085 module
'''
from __future__ import unicode_literals
import json
import time
import unittest

from flask import Flask
from pitools.sensors import bmp085
from Adafruit_BMP.BMP085 import BMP085

app = Flask(__name__)
app.register_blueprint(bmp085.blueprint)


class BMP085TestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_01_setup_bmp085(self):
        '''
        setup_bmp085() shoud return an opened BMP085 instance
        '''
        assert isinstance(bmp085.setup_bmp085(), BMP085)

    def test_02_read_temperature(self):
        '''
        read_temperature API
        '''
        rv = self.app.post('/bmp085/temperature')
        print rv.status_code
        assert 405 == rv.status_code
        rv = self.app.get('/bmp085/temperature')
        data = json.loads(rv.data)
        assert 'temperature' in data
        assert 'pressure' not in data
        assert data['timestamp'] < time.time()

    def test_03_read_pressure(self):
        '''
        read_pressure API
        '''
        rv = self.app.post('/bmp085/pressure')
        print rv.status_code
        assert 405 == rv.status_code
        rv = self.app.get('/bmp085/pressure')
        data = json.loads(rv.data)
        assert 'temperature' not in data
        assert 'pressure' in data
        assert data['timestamp'] < time.time()

    def test_04_read_all(self):
        '''
        read_all API
        '''
        rv = self.app.post('/bmp085/all')
        assert 405 == rv.status_code
        rv = self.app.get('/bmp085/all')
        data = json.loads(rv.data)
        assert 'temperature' in data
        assert 'pressure' in data
        assert data['timestamp'] < time.time()

    def test_05_read_root(self):
        '''
        Should fail with 404 for bmp085 root path
        '''
        rv = self.app.post('/bmp085')
        assert 404 == rv.status_code
        rv = self.app.get('/bmp085')
        assert 404 == rv.status_code

if __name__ == '__main__':
    unittest.main()
