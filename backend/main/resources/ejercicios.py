from flask_restful import Resource
from flask import request

EJERCICIOS = {
    1: {"nombre": "Sentadilla asistida", "descripcion": "Fortalecimiento de piernas"},
    2: {"nombre": "Puente de glúteos", "descripcion": "Fortalecimiento lumbar"},
    3: {"nombre": "Movilidad de hombro", "descripcion": "Ejercicio de movilidad"},
}


class ejercicios(Resource):
    def get(self):
        return EJERCICIOS, 200
