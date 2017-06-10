#!/usr/bin/env python

import socket
import json

import random

import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

from flask import Flask, Response
import time

import pyModeS as pms


from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, (str,bytes)):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, (str,bytes)):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

app = Flask(__name__)
app.debug = True
sock = socket.socket()
sock.connect(('127.0.0.1', 30002))


def event():
    """EventSource stream; server side events. Used for
    constantly making new rolls and sending that roll to
    everyone.

    Returns:
        json event (str): --

    See Also:
        stream()

    """

    LAT = 52.077731
    LONG = 4.39232388

    while True:
        raw_data = sock.recv(40)
        if not raw_data:
            break

        data = []
        print(raw_data)
        msgs = raw_data.split(b'\n')
        for msg in msgs:
            try:
                msg = msg.decode('utf-8')
                msg = msg.rstrip(';')
                msg = msg.lstrip('*')
                pos = pms.adsb.surface_position_with_ref(msg, LAT, LONG)
                d = {'lat': pos[0], 'lng': pos[1]}
                data.append(d)
            except Exception as e:
                #print('exception %s' % e)
                pass

        if data != []:
            yield "data: {}\n\n".format(json.dumps(data))

        with app.app_context():
            gevent.sleep(0.2)


@app.route('/stream/', methods=['GET', 'POST'])
@crossdomain(origin='*')
def stream():
    """SSE (Server Side Events), for an EventSource. Send
    the event of a new message.

    See Also:
        event()

    """

    return Response(event(), mimetype="text/event-stream")


if __name__ == '__main__':
    WSGIServer(('', 5000), app).serve_forever()
