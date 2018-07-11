#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado
from tornado import autoreload
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
from application import app
import os

enable_pretty_logging()

PORT = 80

# ------- PRODUCTION CONFIG -------
# http_server = HTTPServer(WSGIContainer(app))
# http_server.listen(PORT)
# IOLoop.instance().start()


# ------- DEVELOPMENT CONFIG -------
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 80)), debug=True)
