from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api.prefix}/auth/token")
