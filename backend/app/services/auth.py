import datetime
import bcrypt
from jose import JWTError, jwt
from typing import Optional
from app.config.settings import settings

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            # bcrypt membutuhkan input bytes untuk plain_password dan hashed_password
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        # Menghasilkan hash bcrypt berbentuk string
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        # Refresh token berlaku selama 7 hari
        expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, expected_type: str = "access") -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            # Verifikasi type token (access/refresh)
            token_type = payload.get("type")
            if token_type != expected_type:
                return None
                
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
