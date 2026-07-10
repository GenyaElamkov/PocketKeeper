from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширование пароля."""
    return pwd_context.hash(password)


def verify_password(plane_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(plane_password, hashed_password)
