from flask import request
from flask_restful import Resource

from models.run import Run


class Runs(Resource):
    def post(self, id):
        run = Run.get(id)

        if not run:
            return "", 404

        run.update(request.get_json())

        return "", 201
