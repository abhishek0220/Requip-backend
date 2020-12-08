from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def get_user_id_with_jwt():
    verify_jwt_in_request()
    return get_jwt_identity()