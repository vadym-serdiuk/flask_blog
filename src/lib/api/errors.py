class Error(tuple):
    def __new__(cls, code, message, status_code):
        error = dict(status='Error',
                     error_code=code,
                     error_message=message)
        return super(Error, cls).__new__(cls, (error, status_code))
