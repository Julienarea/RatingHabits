import bcrypt

def hash_password(password: str) -> str:
    """
    Хеширует пароль с использованием bcrypt.
    
    Args:
        password (str): Исходный пароль
        
    Returns:
        str: Хеш пароля в виде строки (включая соль)
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли пароль хешу.
    
    Args:
        plain_password (str): Введённый пользователем пароль
        hashed_password (str): Хеш из базы данных
        
    Returns:
        bool: True, если пароль верный
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )