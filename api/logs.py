from flask import request
from flask_restful import Resource

from models.benchmark_group_execution import BenchmarkGroupExecution
from models.memory_usage import MemoryUsage
from logger import log

log_type_class = {
    "BenchmarkGroupExecution": BenchmarkGroupExecution,
    "MemoryUsage": MemoryUsage,
}


class Logs(Resource):
    def post(self):
        data = request.get_json()
        log.info(data)
        log_type_class[data.pop("type")].create(data)
        return "", 201
