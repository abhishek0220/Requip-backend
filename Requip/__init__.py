from flask import Flask, url_for
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
import os, shutil
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
cors = CORS(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per second",]
)
api = Api(app)
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['PROPAGATE_EXCEPTIONS'] = True
jwt = JWTManager(app)
mongo = PyMongo(app)
db = mongo.db

@app.route('/')
def hdfd():
    return "Running..."

from Requip.Resources import user, saman
api.add_resource(user.UserRegistration, '/registration')
api.add_resource(user.UserLogin, '/login')
api.add_resource(user.UserProfile, '/profile/<string:username>')
api.add_resource(user.UserProfileUpdate, '/edit/profile')
api.add_resource(user.TokenRefresh, '/refreshToken')
api.add_resource(user.User, '/profile')
api.add_resource(user.UserReset, '/reset/<string:username>')
api.add_resource(user.UserVerify, '/verify/<string:username>')
api.add_resource(user.ChangeProfilePic, '/edit/profile/pic')
api.add_resource(saman.addSaman, '/add')
api.add_resource(saman.SingleSaman, '/saman/<string:id>')
api.add_resource(saman.listallsaman, '/saman')
api.add_resource(saman.userSaman, '/myposts')
api.add_resource(saman.flagsaman, '/flag/<string:id>')
