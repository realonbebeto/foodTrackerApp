from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWSError, jwt
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .database import get_db
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRECT_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def createAccessToken(data: dict):
    payload = data.copy()
    # datetime.utcnow()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})

    encoded = jwt.encode(payload, SECRECT_KEY, algorithm=ALGORITHM)

    return encoded


def verifyAccessToken(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRECT_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = TokenData(id=id)

    except JWSError:
        raise credentials_exception

    return token_data


def getCurrentUser(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not valid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verifyAccessToken(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
