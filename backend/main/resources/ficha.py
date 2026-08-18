from flask_restful import Resource
from flask import request

FICHA = {
    1: {"paciente": "Juan Perez", "estado": "activo"},
    2: {"paciente": "Maria Lopez", "estado": "alta"},
    3: {"paciente": "Carlos Diaz", "estado": "pendiente"},
}


class ficha(Resource):
    def get(self, id):
        if id in FICHA:
            return FICHA[id], 200
        return "Usuario no encontrado", 404

    def put(self, id):
        if id in FICHA:
            data = request.get_json() or {}
            ficha = FICHA[id]
            ficha.update(data)
            return "Ficha actualizado con exito", 200
        return "No se encontro el usuario", 404

    def delete(self, id):
        if id in FICHA:
            del FICHA[id]
            return "Ficha eliminada con exito", 200
        return "Ficha no encontrada", 404


class fichas(Resource):
    def get(self):
        return FICHA, 200

    def post(self):
        data = request.get_json() or {}
        id = max(FICHA.keys(), default=0) + 1
        FICHA[id] = data
        return FICHA[id], 201
