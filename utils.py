import uuid


def generate_uuid():
    return uuid.uuid4().hex


class UnauthorizedException(Exception):
    pass
