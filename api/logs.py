from flask import request
from flask_restful import Resource

from api.auth import api_access_token_required
from logger import log
from models.benchmark_group_execution import BenchmarkGroupExecution
from models.memory_usage import MemoryUsage
from utils import UnauthorizedException

log_type_class = {
    "BenchmarkGroupExecution": BenchmarkGroupExecution,
    "MemoryUsage": MemoryUsage,
}


class Logs(Resource):
    @api_access_token_required
    def post(self, current_machine):
        try:
            data = request.get_json()
            log.info(data)
            log_class = log_type_class[data.pop("type")]
            log_class.validate_data(current_machine, data)
            log_class.create(data)
            return "", 201
        except UnauthorizedException as e:
            log.exception(e)
            return "Unauthorized", 401
