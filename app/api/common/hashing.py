from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt", deprecated="auto")

def hash_password(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.

    :param password: Пароль в текстовом виде.
    :return: Захэшированный пароль.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли предоставленный пароль хэшу.

    :param plain_password: Оригинальный пароль в текстовом виде.
    :param hashed_password: Захэшированный пароль.
    :return: True, если пароль верен, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)
