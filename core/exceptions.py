
class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = "Usuário já cadastrado!"):
        super().__init__(message=message, status_code=400)

class UserNotFoundError(AppException):
    def __init__(self, message: str = "Usuário não encontrado"):
        super().__init__(message=message, status_code=404)

class InvalidCredentialsError(AppException):
    def __init__(self, message: str = "Usuário ou senha incorretos"):
        super().__init__(message=message, status_code=401)  # status_code 401

class EmailAlreadyExists(AppException):
    def __init__(self, message: str = "Email já cadastrado!"):
        super().__init__(message=message, status_code=409)

class UsernameAlreadyExists(AppException):
    def __init__(self, message: str = "Username já cadastrado!"):
        super().__init__(message=message, status_code=409)