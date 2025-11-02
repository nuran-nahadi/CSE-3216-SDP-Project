from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_database_session
from app.core.dependencies import get_current_user
from app.services.user_profile import UserProfileService
from app.schemas.users import (
    UserProfileResponse, UserProfileUpdate, UserPreferencesResponse, 
    UserPreferencesUpdate, MessageResponse
)
from app.models.models import User


router = APIRouter(tags=["User Profile"], prefix="/users")


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Retrieve the profile information of the currently authenticated user"
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user())
):
    """Get current user profile"""
    return UserProfileService.get_user_profile(current_user)


@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
    summary="Update user profile",
    description="Update the profile information of the currently authenticated user"
)
def update_user_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Update user profile"""
    return UserProfileService.update_user_profile(db, current_user, profile_data)


@router.post(
    "/me/avatar",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
    summary="Upload profile picture",
    description="Upload a new profile picture for the current user"
)
async def upload_profile_picture(
    file: UploadFile = File(..., description="Profile picture file (jpg, jpeg, png, gif, webp)"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Upload profile picture"""
    return await UserProfileService.upload_user_avatar(db, current_user, file)


@router.delete(
    "/me/avatar",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Remove profile picture",
    description="Remove the current user's profile picture"
)
def remove_profile_picture(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Remove profile picture"""
    return UserProfileService.remove_user_avatar(db, current_user)


@router.get(
    "/me/preferences",
    status_code=status.HTTP_200_OK,
    response_model=UserPreferencesResponse,
    summary="Get user preferences",
    description="Retrieve the preferences of the currently authenticated user"
)
def get_user_preferences(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Get user preferences"""
    return UserProfileService.get_user_preferences(db, current_user)


@router.put(
    "/me/preferences",
    status_code=status.HTTP_200_OK,
    response_model=UserPreferencesResponse,
    summary="Update user preferences",
    description="Update the preferences of the currently authenticated user"
)
def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Update user preferences"""
    return UserProfileService.update_user_preferences(db, current_user, preferences_data)


@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
    summary="Delete user account",
    description="Permanently delete the current user's account and all associated data"
)
def delete_user_account(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user())
):
    """Delete user account"""
    return UserProfileService.delete_user_account(db, current_user)
