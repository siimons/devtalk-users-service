from fastapi import HTTPException


class UserBaseException(Exception):
    """Базовое исключение для всех ошибок, связанных с пользователями"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(UserBaseException):
    """Исключение для ситуации, когда пользователь не найден"""
    
    def __init__(self, user_id: int):
        message = f"Пользователь с ID {user_id} не найден."
        super().__init__(message)


class UserAlreadyExistsException(UserBaseException):
    """Исключение для ситуации, когда пользователь с таким email уже существует"""
    
    def __init__(self, email: str):
        message = f"Пользователь с email \"{email}\" уже существует."
        super().__init__(message)


class InvalidCredentialsException(UserBaseException):
    """Исключение для недействительных учетных данных"""
    
    def __init__(self):
        message = "Неверный email или пароль."
        super().__init__(message)


class UserUpdateException(UserBaseException):
    """Исключение для ошибки при обновлении информации о пользователе"""
    
    def __init__(self, user_id: int):
        message = f"Ошибка при обновлении данных пользователя с ID {user_id}."
        super().__init__(message)


class UserDeletionException(UserBaseException):
    """Исключение для ошибки удаления пользователя"""
    
    def __init__(self, user_id: int):
        message = f"Ошибка при удалении пользователя с ID {user_id}."
        super().__init__(message)


# HTTPException генераторы

def user_not_found_exception(user_id: int):
    """Обрабатывает исключение, когда пользователь не найден"""
    return HTTPException(
        status_code=404,
        detail=f"Пользователь с ID {user_id} не найден."
    )


def user_already_exists_exception(email: str):
    """Обрабатывает исключение, когда пользователь с таким email уже существует"""
    return HTTPException(
        status_code=400,
        detail=f"Пользователь с email \"{email}\" уже существует."
    )


def invalid_credentials_exception():
    """Обрабатывает исключение для недействительных учетных данных"""
    return HTTPException(
        status_code=401,
        detail="Неверный email или пароль."
    )


def user_update_exception(user_id: int):
    """Обрабатывает исключение при ошибке обновления информации о пользователе"""
    return HTTPException(
        status_code=500,
        detail=f"Ошибка при обновлении данных пользователя с ID {user_id}."
    )


def user_deletion_exception(user_id: int):
    """Обрабатывает исключение при ошибке удаления пользователя"""
    return HTTPException(
        status_code=500,
        detail=f"Ошибка при удалении пользователя с ID {user_id}."
    )
