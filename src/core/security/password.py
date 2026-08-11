from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Хеширование пароля."""
    return password_hash.hash(password)


def verify_password(plane_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return password_hash.verify(plane_password, hashed_password)
