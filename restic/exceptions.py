"""
Exception classes.
"""
class APIException(Exception):
    """
    Generic exception class.

    Defaults to "Server Error".
    """
    status = 500
    message = 'Server error'
    details = None

    def __init__(self, message=None, details=None):
        if message is not None:
            self.message = message
        self.details = details
        super(APIException, self).__init__(self)


class BadRequest(APIException):
    """
    "Bad Request" exception.
    """
    status = 400
    message = 'Bad Request'


class Unauthorized(APIException):
    """
    "Unauthorized" exception.
    """
    status = 401
    message = 'Unauthorized'


class Forbidden(APIException):
    """
    "Forbidden" exception.
    """
    status = 403
    message = 'Forbidden'


class NotFound(APIException):
    """
    "Not Found" exception.
    """
    status = 404
    message = 'Not Found'


class MethodNotAllowed(APIException):
    """
    "Method Not Allowed" exception.
    """
    status = 405
    message = 'Method Not Allowed'
