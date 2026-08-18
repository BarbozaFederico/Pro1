from flask_restful import Resource
from flask import request

AUTH = {
    1: {"usuario": "admin", "password": "1234"},
    2: {"usuario": "cliente", "password": "abcd"},
    3: {"usuario": "invitado", "password": "guest"},
}


class login(Resource):
    def post(self):
        data = request.get_json() or {}
        id = max(AUTH.keys(), default=0) + 1
        AUTH[id] = data
        return AUTH[id], 201


class Register(Resource):
    def post(self):
        data = request.get_json() or {}
        id = max(AUTH.keys(), default=0) + 1
        AUTH[id] = data
        return AUTH[id], 201
