from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
import os
from flask_pymongo import PyMongo



app = Flask(__name__)
api = Api(app)
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)
mongo = PyMongo(app)
db = mongo.db

from Requip.Resources import user
api.add_resource(user.UserRegistration, '/registration')
api.add_resource(user.UserLogin, '/login')
api.add_resource(user.UserProfile, '/profile/<string:username>')
api.add_resource(user.UserProfileUpdate, '/profile/updateprofile')
