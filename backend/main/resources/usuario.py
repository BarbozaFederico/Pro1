from flask_restful import Resource
from flask import request

USUARIO = {
	1: {"nombre": "Ana", "email": "ana@mail.com"},
	2: {"nombre": "Luis", "email": "luis@mail.com"},
	3: {"nombre": "Sofia", "email": "sofia@mail.com"},
}

class usuario (Resource):
    def get(self, id):
        if id in USUARIO:
            return USUARIO[id], 200
        return "usuario no encontrado",404
    def put(self, id):
        if id in USUARIO:
            data = request.get_json() or {}
            usuario = USUARIO[id]
            usuario.update(data)
            return "Usuario actualizado con exito",200
        return "Usuario no existente",404
        
    def delete(self, id):
         if id in USUARIO:
             del USUARIO[id]
             return "Usuario eliminado con exito",200
         return "Usuario no encontrado",404
        
class usuarios (Resource):
    def get(self):
        return USUARIO, 200
    def post(self):
        data = request.get_json() or {}
        id = max(USUARIO.keys(), default=0) + 1
        USUARIO[id] = data
        return USUARIO[id], 201 
    
    


