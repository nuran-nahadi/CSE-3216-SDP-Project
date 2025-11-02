from fastapi import APIRouter, Depends, status, Header
from sqlalchemy.orm import Session
from app.services.auth import AuthService
from app.core.dependencies import get_database_session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.schemas.auth import UserOut, Signup


router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/signup", status_code=status.HTTP_200_OK, response_model=UserOut)
async def user_login(
        user: Signup,
        db: Session = Depends(get_database_session)):
    return await AuthService.signup(db, user)


@router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(
        user_credentials: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_database_session)):
    
    # Expected response after login
    # {
    #  "access_token": "eyJhbGciOiJIUzI1...",
    #  "refresh_token": "eyJhbGciOiJIUzI1...",
    #  "token_type": "Bearer",
    #  "expires_in": 3600
    # }
    
    return await AuthService.login(user_credentials, db)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
        refresh_token: str = Header(),
        db: Session = Depends(get_database_session)):
    return await AuthService.get_refresh_token(token=refresh_token, db=db)
