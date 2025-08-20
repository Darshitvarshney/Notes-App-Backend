import jwt
import datetime
from functools import wraps
import os
from flask import request, jsonify
from bson import ObjectId

from backend.models.adminModel import Admin
from backend.models.collaboratorModel import Collaborator

JWT_SECRET = "darshitdev2005"
JWT_EXPIRY_HOURS = 72

def generate_token(admin):
    payload = {
        "_id": str(admin.id),
        "email": admin.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS)
    }
    print(payload)
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")




def token_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"message": "Token is missing", "status": 401}), 401
        try:
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            admin = Admin.objects(id=data["_id"]).first()
            if not admin:
                return jsonify({"message": "Admin not found", "status": 404}), 404
            request.admin = admin
        except Exception as e:
            return jsonify({"message": "Invalid or expired token", "status": 401, "error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated


def token_user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"message": "Token is missing", "status": 401}), 401
        try:
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            collaborator = Collaborator.objects(id=data["_id"]).first()
            if not collaborator:
                return jsonify({"message": "Admin not found", "status": 404}), 404
            request.admin = collaborator
        except Exception as e:
            return jsonify({"message": "Invalid or expired token", "status": 401, "error": str(e)}), 401
        current_user = data
        return f(current_user,*args, **kwargs)
    return decorated

def serialize_doc(doc):
    if hasattr(doc, "to_mongo"):  # Document or EmbeddedDocument
        d = doc.to_mongo().to_dict()
        return serialize_doc(d)  # recurse

    elif isinstance(doc, dict):
        out = {}
        for k, v in doc.items():
            if k == "_id":  # rename Mongo's _id
                out["id"] = str(v)
            else:
                out[k] = serialize_doc(v)
        return out

    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]

    elif isinstance(doc, ObjectId):
        return str(doc)

    else:
        return doc

