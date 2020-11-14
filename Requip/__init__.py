from flask import Flask, url_for
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
import os, shutil
from flask_pymongo import PyMongo

app = Flask(__name__)
cors = CORS(app)
api = Api(app)
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
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
api.add_resource(user.ChangeProfilePic, '/edit/profile/pic')
api.add_resource(saman.addSaman, '/saman/addsaman')
api.add_resource(saman.editsaman, '/saman/editsaman')
api.add_resource(saman.deletesaman, '/saman/deletesaman')
api.add_resource(saman.listallsaman, '/saman')
api.add_resource(saman.singleSaman, '/saman/<string:id>')