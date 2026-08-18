from flask_restful import Resource
from flask import request

PLAN = {
    1: {"nombre": "Plan Basico", "precio": 10000},
    2: {"nombre": "Plan Plus", "precio": 18000},
    3: {"nombre": "Plan Premium", "precio": 25000},
}


class planes(Resource):
    def get(self):
        return PLAN, 200

    def post(self):
        data = request.get_json() or {}
        id = max(PLAN.keys(), default=0) + 1
        PLAN[id] = data
        return PLAN[id], 201


class plan(Resource):
    def get(self, id):
        if id in PLAN:
            return PLAN[id], 200
        return "Plan no encontrado", 404

    def put(self, id):
        if id in PLAN:
            data = request.get_json() or {}
            plan = PLAN[id]
            plan.update(data)
            return "Plan actualizado cone exito", 200
        return "Plan no encontrado", 404

    def delete(self, id):
        if id in PLAN:
            del PLAN[id]
            return "Plan eliminado con exito", 200
        return "Plan no encontrado", 404
