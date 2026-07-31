

class AppException(Exception):
    """Classe base para todas as exceções de negócio da aplicação"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsError(AppException):
    pass


class UserNotFoundError(AppException):
    pass