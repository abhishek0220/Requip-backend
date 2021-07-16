from flask_restful import Resource, reqparse, request
from flask import Response
from Requip import limiter
import requests
import os


TWQ_CODE = os.environ['TWOWAYQR']

def twqgetUser(resp: str):
    res = requests.post(
        'https://twowayqr.iamabhishek.live/authorize',
        json={
            'response_qr': resp
        },
        headers={ 'vendor-secret': TWQ_CODE}
    )
    if res.status_code == 200:
        return res.json()
    else:
        print(res.status_code)
        print(res.json())
    return None
    

class GetAUTHID(Resource):
    decorators = [limiter.limit("5/second")]
    def get(self):
        query = request.args.get('scopes')
        if query is None:
            return Response( 'Please pass scopes in query', status=400)
        res = requests.get(
            f'https://twowayqr.iamabhishek.live/auth-id?scopes={query}',
            headers={ 'vendor-secret': TWQ_CODE}
        )
        try:
            rjson = res.json()
        except:
            return Response("Some error occured", status=500) 
        if res.status_code != 200:
            return Response(rjson, status=res.status_code)
        else:
            return {
                "qr": rjson['qr'],
                "token":rjson['token']
            }
