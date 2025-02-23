from fastapi import HTTPException

class ServiceException(Exception):
    """Базовый класс для всех исключений сервиса"""
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_http(self):
        """Преобразует исключение в HTTPException"""
        return HTTPException(status_code=self.code, detail=self.message)


class UserNotFoundException(ServiceException):
    """Исключение для ситуации, когда пользователь не найден"""
    def __init__(self, user_id: int):
        super().__init__(f"Пользователь с ID {user_id} не найден.", 404)


class UserAlreadyExistsException(ServiceException):
    """Исключение для ситуации, когда пользователь с таким email уже существует"""
    def __init__(self, email: str):
        super().__init__(f"Пользователь с email {email} уже существует.", 400)


class InvalidCredentialsException(ServiceException):
    """Исключение для недействительных учетных данных"""
    def __init__(self):
        super().__init__("Неверный email или пароль.", 401)


class UserUpdateException(ServiceException):
    """Исключение для ошибки при обновлении информации о пользователе"""
    def __init__(self, user_id: int):
        super().__init__(f"Ошибка при обновлении данных пользователя с ID {user_id}.", 500)


class TooManyRequestsException(ServiceException):
    """Исключение для защиты от частых запросов (Brute Force)"""
    def __init__(self, retry_after: int):
        super().__init__(
            f"Слишком много запросов. Попробуйте снова через {retry_after} секунд.",
            429
        )
        self.retry_after = retry_after

    def to_http(self):
        """Переопределяет метод для добавления заголовка Retry-After"""
        return HTTPException(
            status_code=self.code,
            detail=self.message,
            headers={"Retry-After": str(self.retry_after)}
        )


class UserDeletionException(ServiceException):
    """Исключение для ошибки удаления пользователя"""
    def __init__(self, user_id: int):
        super().__init__(f"Ошибка при удалении пользователя с ID {user_id}.", 500)