import bcrypt


def hash_value(value: str) -> str:
    """
    Хэширует переданное значение с использованием bcrypt.

    Args:
        value (str): Значение в текстовом виде.

    Returns:
        str: Захэшированное значение.
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(value.encode('utf-8'), salt).decode('utf-8')


def verify_value(plain_value: str, hashed_value: str) -> bool:
    """
    Проверяет, соответствует ли переданное значение его хэшу.

    Args:
        plain_value (str): Оригинальное значение в текстовом виде.
        hashed_value (str): Захэшированное значение.

    Returns:
        bool: True если значение соответствует хэшу, иначе False.

    Raises:
        ValueError: Если переданные значения не могут быть обработаны.
    """
    try:
        return bcrypt.checkpw(
            plain_value.encode('utf-8'),
            hashed_value.encode('utf-8')
        )
    except (ValueError, TypeError):
        return False