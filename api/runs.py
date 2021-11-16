from flask import request
from flask_restful import Resource

from api.auth import api_access_token_required
from models.run import Run


class Runs(Resource):
    @api_access_token_required
    def post(self, current_machine, id):
        run = Run.first(id=id, machine_name=current_machine.name)

        if not run:
            return "", 404

        run.update(request.get_json())

        return "", 201
