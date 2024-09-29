from fastapi import HTTPException

class AppBaseException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
'''Базовое исключение для проекта'''

class UserAlreadyExistsException(AppBaseException):
    def __init__(self, email: str):
        message = f"Пользователь с email {email} уже существует."
        super().__init__(message)
'''Исключение для ситуации, когда пользователь уже существует'''

class UserNotFoundException(AppBaseException):
    def __init__(self, user_id: int):
        message = f"Пользователь с ID {user_id} не найден."
        super().__init__(message)
'''Исключение для случая, если пользователь не найден'''

class AuthenticationFailedException(AppBaseException):
    def __init__(self):
        message = "Ошибка аутентификации. Проверьте логин и пароль."
        super().__init__(message)
'''Исключение для неудачной аутентификации'''

def user_already_exists_exception(email: str):
    return HTTPException(status_code=400, detail=f"Пользователь с email {email} уже существует.")

def user_not_found_exception(user_id: int):
    return HTTPException(status_code=404, detail=f"Пользователь с ID {user_id} не найден.")

def authentication_failed_exception():
    return HTTPException(status_code=401, detail="Неверные учетные данные.")
'''Преобразование пользовательских исключений в HTTP-исключения'''
