import datetime

from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from starlette import status

from ..library.users import find_user


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
    secret = 'supersecret'

    def get_password_hash(self, password):
        """Return a hashed version of a password."""
        return self.pwd_context.hash(password)

    def verify_password(self, pwd, hashed_pwd):
        """Return True if hashed version of password is verified."""
        return self.pwd_context.verify(pwd, hashed_pwd)

    def encode_token(self, user_id):
        """Create an encoded JSON Web Token (JWT)."""
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode_token(self, token):
        """Decode an encoded JSON Web Token (JWT)."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(status_code=401, detail="Expired signature") from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        """Authentication wrapper."""
        return self.decode_token(auth.credentials)

    def get_current_user(self, auth: HTTPAuthorizationCredentials = Security(security)):
        """Return current authorised user"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
        username = self.decode_token(auth.credentials)
        if username is None:
            raise credentials_exception
        user = find_user(username)
        if user is None:
            raise credentials_exception
        return user
