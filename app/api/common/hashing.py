from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt", deprecated="auto")


def hash_value(value: str) -> str:
    """
    Хэширует переданное значение с использованием bcrypt.

    Args:
        value (str): Значение в текстовом виде.

    Returns:
        str: Захэшированное значение.
    """
    return pwd_context.hash(value)


def verify_value(plain_value: str, hashed_value: str) -> bool:
    """
    Проверяет, соответствует ли переданное значение его хэшу.

    Args:
        plain_value (str): Оригинальное значение в текстовом виде.
        hashed_value (str): Захэшированное значение.

    Returns:
        bool: True, если значение верно, иначе False.
    """
    return pwd_context.verify(plain_value, hashed_value)
