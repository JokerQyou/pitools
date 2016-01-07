# coding: utf-8
from __future__ import unicode_literals
import unittest
import tempfile
import shutil

from flask import Flask
from pitools import camera

app = Flask(__name__)
app.register_blueprint(camera.blueprint)


class CameraTestCase(unittest.TestCase):

    def setUp(self):
        self.workspace = tempfile.mkdtemp()
        self.app = app.test_client()

    def tearDown(self):
        shutil.rmtree(self.workspace)

    def test_post_shot_api(self):
        '''
        Should fail with 405 with GET request
        '''
        rv = self.app.post('/camera/shot')
        assert 405 == rv.status_code

    def test_get_shot_api(self):
        '''
        Should return a image with MIME of image/*
        '''
        rv = self.app.get('/camera/shot')
        assert rv.content_type.startswith('image/')
        print dir(rv)

if __name__ == '__main__':
    unittest.main()
