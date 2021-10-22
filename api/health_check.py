from flask_restful import Resource


class HealthCheck(Resource):
    def get(self):
        return {"success": True}, 200
