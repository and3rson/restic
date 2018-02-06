"""
Exception classes.
"""
class APIException(Exception):
    """
    Generic exception class.

    Defaults to "Server Error".
    """
    status = 500
    detail = 'Server error'

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = detail
        super(APIException, self).__init__(self)


class BadRequest(APIException):
    """
    "Bad Request" exception.
    """
    status = 400
    detail = 'Bad Request'


class Unauthorized(APIException):
    """
    "Unauthorized" exception.
    """
    status = 401
    detail = 'Unauthorized'


class Forbidden(APIException):
    """
    "Forbidden" exception.
    """
    status = 403
    detail = 'Forbidden'


class NotFound(APIException):
    """
    "Not Found" exception.
    """
    status = 404
    detail = 'Not Found'


class MethodNotAllowed(APIException):
    """
    "Method Not Allowed" exception.
    """
    status = 405
    detail = 'Method Not Allowed'
