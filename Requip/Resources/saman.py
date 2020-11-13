from flask_restful import Resource, reqparse
from flask import Response
from Requip import db
import uuid
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

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
        parser.add_argument('tag', help = 'This field cannot be blank', required = True)
        parser.add_argument('brand', help = 'This field can be blank', required = False)
        parser.add_argument('description', help = 'This field can be blank', required = False)
        parser.add_argument('address', help = 'This field can be blank', required = False)

        data = parser.parse_args()
        _price = data['price']
        _brand = data['brand']
        _discription = data['description']
        _title = data['title']
        _tag = data['tag']
        _address = data['address']

        saman = {}

        saman['_id'] = str(uuid.uuid4())
        saman["username"] = username
        saman['price'] = _price
        saman['tag']   = _tag
        saman["title"] = _title
        if _brand != None:
            saman['brand'] = _brand
        else:
            saman['brand'] = ""
        if _discription != None:
            saman['discription'] = _discription
        else:
            saman['discription'] = _brand
        if _address != None:
            saman['address'] = _address
        else:
            print("there is no address mentioned of this saman {} ".format(_title))


        if (db.saman.find_one({"username" : username}) and db.saman.find_one({"title" : _title})):
            return {"message" : "The title exsists for the current user, Please use the different title to identify your Saaman"}
        else:
            try :
                db.saman.insert_one(saman)
                return {"message":"new post of saaman is created successfully..!!"}
            except Exception as e:
                return {"message" :"error occured, {}".format(e)}

class editsaman(Resource):
    @jwt_required
    def post(self):
        username = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('titleOld', help = 'This field canot be blank', required = True)
        parser.add_argument('titleNew', help = 'This field can be blank', required = False)
        parser.add_argument('description', help = 'This field can be blank', required = False)
        parser.add_argument('price', help = 'This field can be blank', required = False)
        parser.add_argument('brand', help = 'This field can be blank', required = False)
        parser.add_argument('tag', help = 'This field can be blank', required = False)
        parser.add_argument('address', help = 'This field can be blank', required = False)

        data = parser.parse_args()
        _title_old = data['titleOld']
        _title_new = data['titleNew']
        _discription = data['description']
        _price = data['price']
        _brand = data['brand']
        _tag = data['tag']
        _address = data['address']

        query = {'username': username, "title": _title_old}
        saman_values = {}
        saman_values["username"] = username



        if (db.saman.find_one(db.saman.find_one(query))):
            if _title!=None:
                saman_values["title"] = _title_new
            else:
                saman_values["title"] = _title_old
            if _price != None:
                saman_values['price'] = _price
            else:
                saman_values["price"] = ""
            if _tag != None:
                saman_values['tag']   = _tag
            else:
                saman_values["tag"] = ""
            if _brand != None:
                saman_values['brand'] = _brand
            else:
                saman_values["brand"] = ""
            if _discription != None:
                saman_values['discription'] = _discription
            else:
                saman_values["description"] = ""
            if _address != None:
                saman_values['address'] = _address
            else:
                saman_values["address"] = ""

            query_update = { "$set": saman_values }

            try:
                db.saman.update_one(query, query_update)
                return {"message" : "Information of your saman updated successfully"}
            except Exception as e:
                print("could not able to update the info of saaman")
                print("Exception", e)
                return {"message": "Sorry due to some reason the information of your saman is not updated..!!"}

class deletesaman(Resource):
    @jwt_required
    def delete(self):
        username = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('title', help = 'This field canot be blank', required = True)

        data = parser.parse_args()
        _title = data['title']

        query = {'username': username, "title": _title}

        try:
            db.saman.delete_one(query)
            return {"message" : "Your saaman's post has been deleted successfully..!!"}
        except Exception as e:
            return {"message" : "Post is not deleted successfully, error is -> {} ".format(e)}

class listallsaman(Resource):
    def get(self):
        total_saman = []
        try:
            saman_list = db.saman.find()
        except Exception as e:
            return {'message':"error occured while loading, error is -> {} ".format(e)}

        for i in saman_list:
            total_saman.append(i)

        return total_saman

class singleSaman(Resource):
    def get(self, id):
        try:
            return db.saman.find_one({"_id" : id})
        except Exception as e:
            return {'message':"error occured while loading, error is -> {} ".format(e)}
