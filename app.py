from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
import os
from flask_pymongo import PyMongo

load_dotenv()

app = Flask(__name__)
api = Api(app)
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)
mongo = PyMongo(app)
db = mongo.db

import resources
api.add_resource(resources.UserRegistration, '/registration')
