from flask_restful import Resource, reqparse, request
from flask import Response
from Requip import db
import uuid, base64
from io import BytesIO
from PIL import Image
import os, json
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, verify_jwt_in_request_optional)
from Requip.azureStorage import FileManagement

'''
contains four methods for saman
1. to create a advertisement to sell saman
2. to delete a advertisement from saman
3. to edit the advertisement for saman
4. to return list of all saman advertisement
'''


class addSaman(Resource):
    @jwt_required
    def post(self):
        username = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('title', help = 'This field cannot be blank', required = True)
        parser.add_argument('price', help = 'This field cannot be blank', required = True)
        parser.add_argument('image', help = 'This field cannot be blank', required = True)
        parser.add_argument('type', help = 'This field can be blank', required = True)
        parser.add_argument('description', help = 'This field can be blank', required = True)
        parser.add_argument('phone', help = 'This field can be blank', required = True)
        data = parser.parse_args()
        post_id = str(uuid.uuid4())
        data['_id'] = post_id
        _user = db.users.find_one({'username': username})
        if(_user == None):
            return Response("{'message': 'User not exist'}", status=404, mimetype='application/json')
        try:
            img_rev = data['image'].split(',')[1]
            image_data = bytes(img_rev, encoding="ascii")
            im = Image.open(BytesIO(base64.b64decode(image_data)))
            if(im.size[0] > 720 or im.size[1] > 720):
                return Response("{'message': 'Invalid Size'}", status=403, mimetype='application/json')
            tar_loc = f'{username}_{str(uuid.uuid4())}.jpg'
            post_img_path = f'{username}/{post_id}/{str(uuid.uuid4())}.jpg'
            file_loc = os.path.join(os.getenv('FILES'),tar_loc)
            im = im.convert("RGB")
            im.save(file_loc)
            FileManagement.upload(post_img_path, file_loc)
            data['images'] = post_img_path
            data['username'] = username
            del data['image']
            os.remove(file_loc)
            db.saman.insert_one(data)
            return {"message":"new post of saaman is created successfully..!!"}
        except:
            return Response("{'message': 'Invalid image'}", status=403, mimetype='application/json')

class SingleSaman(Resource):

    def get_identity_if_logedin(self):
        try:
            verify_jwt_in_request_optional()
            return get_jwt_identity()
        except Exception:
            # this handles if the access tocken is wrong or expired, hence have to handle:-
            pass

    def get(self, id):
        logged_user = self.get_identity_if_logedin()
        item = db.saman.find_one({"_id" : id})
        if(item == None):
            return Response( '404 Not Found', status=404,)
        item['moneytized'] = 'priced'
        if(int(item['price']) == 0):
            item['moneytized'] = 'free'
        # handline if user is loggedin or not to show phone number:-
        if logged_user == None:
            item["phone"] = "xxxxxxxxxx"
        return item

    @jwt_required
    def post(self, id):
        username = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('title', help = 'This field cannot be blank', required = True)
        parser.add_argument('price', help = 'This field cannot be blank', required = True)
        #parser.add_argument('image', help = 'This field cannot be blank', required = False)
        parser.add_argument('type', help = 'This field can be blank', required = True)
        parser.add_argument('description', help = 'This field can be blank', required = True)
        parser.add_argument('phone', help = 'This field can be blank', required = True)
        data = parser.parse_args()
        query = {'username': username, "_id": id}
        if (db.saman.find_one(query)):
            query_update = { "$set": data }
            try:
                db.saman.update_one(query, query_update)
                return {"message" : "Information of your saman updated successfully"}
            except Exception as e:
                print("could not able to update the info of saaman")
                print("Exception", e)
                return Response("{'message': 'Sorry due to some reason the information of your saman is not updated..!!'}", status=403, mimetype='application/json')
        else:
            return Response("{'message': 'You cannot edit this saman'}", status=403, mimetype='application/json')

    @jwt_required
    def delete(self, id):
        username = get_jwt_identity()
        query = {'username': username, "_id": id}
        item = db.saman.find_one(query)
        if(item == None):
            return {'message': 'You cannot edit this saman'}
        try:
            FileManagement.delete(item['images'])
            db.saman.delete_one(query)
            return {"message" : "Your saaman's post has been deleted successfully..!!"}
        except Exception as e:
            return {"message" : "Post is not deleted successfully, error is -> {} ".format(e)}

class flagsaman(Resource):
    @jwt_required
    def post(self, id):
        username = get_jwt_identity()
        item = db.saman.find_one({"_id" : id})
        if(item == None):
            return Response( '404 Not Found', status=404,)
        try:
            count = int(item["flag_count"])
        except :
            count = 0
        query = {"_id": id}
        query_update = { "$set": {"flag_count": count+1 } }
        # handling if the flag is reached certain threshold flag to review by developers.
        if((count+1) >= 10):
            print("This saman is flagged above 10")
        try:
            db.saman.update_one(query, query_update)
            return {"message" : "This saman is flagged"}
        except Exception as e:
            return {"message": "error occured while flagging"}

class listallsaman(Resource):
    def get(self):
        total_saman = []
        query = request.args.get('text', -1)
        objType = request.args.get('type', -1)
        to_get = {'_id' : 1, 'images' : 1, 'title' : 1, 'type' : 1, 'price':1}
        filterBy = {}
        obj_Arr = []
        if(objType != -1):
            obj_Arr = objType.split(',')
        filterBy['type'] = {'$in' : obj_Arr}
        if(query != -1):
            to_get.update({'score': {'$meta': "textScore"}})
            filterBy["$text"] = {"$search": query}
        if(len(filterBy) > 0):
            saman_list = db.saman.find(filterBy, to_get,)
        else:
            saman_list = db.saman.find({}, to_get )
        for i in saman_list:
            total_saman.append(i)
        return total_saman

class userSaman(Resource):
    @jwt_required
    def get(self):
        user_saman = []
        username = get_jwt_identity()
        try:
            query = {'username': username}
            saman_list = db.saman.find(query)
        except Exception as e:
            return {'message':"error occured while loading, error is -> {} ".format(e)}
        for i in saman_list:
            user_saman.append(i)
        return user_saman
