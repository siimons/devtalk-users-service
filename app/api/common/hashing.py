from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt", deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.

    Args:
        password (str): Пароль в текстовом виде.

    Returns:
        str: Захэшированный пароль.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли предоставленный пароль хэшу.

    Args:
        plain_password (str): Оригинальный пароль в текстовом виде.
        hashed_password (str): Захэшированный пароль.

    Returns:
        bool: True, если пароль верен, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)
