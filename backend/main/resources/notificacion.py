from flask_restful import Resource
from flask import request

NOTI = {
    1: {"tipo": "email", "mensaje": "Turno confirmado"},
    2: {"tipo": "sms", "mensaje": "Recordatorio de cita"},
    3: {"tipo": "push", "mensaje": "Nueva notificacion"},
}


class notificaciones(Resource):
    def post(self):
        data = request.get_json() or {}
        id = max(NOTI.keys(), default=0) + 1
        NOTI[id] = data
        return NOTI[id], 201
