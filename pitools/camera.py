# coding: utf-8
from __future__ import unicode_literals

import json
import time
from io import BytesIO

from flask import Blueprint, current_app, request, send_file
from picamera import PiCamera

blueprint = Blueprint('camera', __name__, url_prefix='/camera')
DEFAULT_RESOLUTION = (800, 600)


def setup_camera():
    '''
    Instantiate and return a PiCamera object
    '''
    camera = PiCamera()
    return camera


@blueprint.route('/shot', methods=('GET', ))
def shot():
    '''
    Take a photo
    '''
    if not isinstance(getattr(current_app, 'camera', None), PiCamera):
        setattr(current_app, 'camera', setup_camera())

    annotation = request.args.get(
        'annotation',
        time.strftime('%Y/%m/%d %H:%M:%S')
    )
    try:
        resolution = json.loads(request.args.get('resolution', None))
        if not isinstance(resolution, (list,)) or len(resolution) != 2:
            resolution = DEFAULT_RESOLUTION
    except:
        resolution = DEFAULT_RESOLUTION

    pdata = BytesIO()
    current_app.camera.annotation_text = annotation
    current_app.camera.capture(pdata, resize=resolution, format='jpeg')
    pdata.seek(0)
    return send_file(
        pdata,
        attachment_filename='.'.join([annotation, 'jpeg']),
        mimetype='image/jpeg'
    )
