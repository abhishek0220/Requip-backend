from flask_restful import Resource, reqparse, request
from flask import Response
from Requip import db
import uuid, base64
from io import BytesIO
from PIL import Image
import os, json
import pprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from Requip import limiter
from Requip.Resources.extra import get_user_id_with_jwt

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, verify_jwt_in_request_optional)
from msrest.authentication import CognitiveServicesCredentials

class addEntertainmentrResource(Resource):

    @jwt_required
    def post(self):
        username = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('title', help = 'This field cannot be blank', required = True)
        parser.add_argument('image', help = 'This field cannot be blank', required = True)
        parser.add_argument('description', help = 'This field cannot be blank', required = True)
        parser.add_argument('link', help = 'This field cannot be blank', required = True)
        parser.add_argument('imdbRating', help = 'This field can be blank', required = False)
        data = parser.parse_args()
        post_id = str(uuid.uuid4())
        data['_id'] = post_id
        _user = db.users.find_one({'username': username})
        if(_user == None):
            return Response("{'message': 'User not exist'}", status=404, mimetype='application/json')
        try:
            post = db.entertainment.find_one({"username":username, "link":data["link"]})
            if post != null:
                return Response("{'message': 'This link is added in previously in some of your post.'}", status=403, mimetype='application/json')
            img_rev = data['image'].split(',')[1]
            image_data = bytes(img_rev, encoding="ascii")
            im = Image.open(BytesIO(base64.b64decode(image_data)))
            if(im.size[0] > 720 or im.size[1] > 720):
                return Response("{'message': 'Invalid Size'}", status=403, mimetype='application/json')
            tar_loc = f'{username}_{str(uuid.uuid4())}.jpg'
            post_img_path = f'entertainment/{username}/{post_id}/{str(uuid.uuid4())}.jpg'
            file_loc = os.path.join(os.getenv('FILES'),tar_loc)
            im = im.convert("RGB")
            im.save(file_loc)
            FileManagement.upload(post_img_path, file_loc)
            data['images'] = post_img_path
            data['username'] = username
            del data['image']
            os.remove(file_loc)
            db.entertainment.insert_one(data)
            return {"message":"new post published successfully..!!"}
        except:
            return Response("{'message': 'Invalid image'}", status=403, mimetype='application/json')
