from fastapi.security.http import HTTPAuthorizationCredentials
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import settings
from jose import JWTError, jwt
from app.schemas.auth import TokenResponse
from fastapi import HTTPException, Depends, status
from app.models.models import User
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from app.core.database_manager import db_manager
from app.utils.responses import ResponseHandler


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_scheme = HTTPBearer()



# Create Hash Password
def get_password_hash(password):
    return pwd_context.hash(password)

# Verify Hash Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Helper Function Used In Other Files 
def get_current_user(token):
    user = get_token_payload(token.credentials)
    return user.get('id')




# Create Access Token
async def create_access_token(data: dict, access_token_expiry=None):
    payload = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload.update({"exp": expire})

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


# Create Refresh Token
async def create_refresh_token(data):
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.secret_key, settings.algorithm)


# Create Access & Refresh Token
async def get_user_token(id: int, refresh_token=None):
    payload = {"id": id}

    access_token_expiry = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expiry = timedelta(days=settings.refresh_token_expire_days)

    access_token = await create_access_token(payload, access_token_expiry)

    if not refresh_token:
        refresh_token = await create_refresh_token(payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expiry.seconds,
        refresh_token_expires_in=refresh_token_expiry.seconds
    )




# Get Payload Of Token
def get_token_payload(token):
    try:
        payload = jwt.decode(token, settings.secret_key, [settings.algorithm])
        if datetime.fromtimestamp(payload.get('exp')) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    
    except JWTError:
        raise ResponseHandler.invalid_token('access')


# Check Admin Role
def check_admin_role(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(db_manager.get_db)):
    user = get_token_payload(token.credentials)
    user_id = user.get('id')
    role_user = db.query(User).filter(User.id == user_id).first()
    if role_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")


# Get Current Authenticated User
def get_current_authenticated_user(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(db_manager.get_db)
) -> User:
    """Get the current authenticated user from token"""
    user_data = get_token_payload(token.credentials)
    user_id = user_data.get('id')
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user