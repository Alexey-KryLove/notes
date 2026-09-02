from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        raise ValueError("Ошибка хеширования пароля") from e

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

