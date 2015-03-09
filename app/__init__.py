from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)

# todo esto podria ir en un config.py
app.config["MONGODB_SETTINGS"] = {'DB': "mongoose"}
app.secret_key = 'mongoose' # cambiar...
CSRF_ENABLED = True

#  Mongoengine
db = MongoEngine(app)

# Cifrado de passwords (por defecto con BCRYPT_LOG_ROUNDS=12)
cifrado = Bcrypt(app)

# Requerido por Flask_Login
lm = LoginManager()
lm.init_app(app)

from app import views