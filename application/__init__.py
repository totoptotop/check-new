from flask import Flask, session
import logging
from flask_cache import Cache
from flask_sqlalchemy import SQLAlchemy


app = Flask('application')

# app.config.from_object('config.ProductionConfig')
app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


import views