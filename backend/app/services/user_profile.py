from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from app.models.models import User, UserPreferences
from app.schemas.users import (
    UserProfileOut, UserProfileUpdate, UserPreferencesOut, 
    UserPreferencesUpdate, UserPreferencesBase
)
from app.utils.upload import upload_profile_picture, delete_profile_picture
from app.utils.responses import ResponseHandler
from typing import Optional
import json
from uuid import UUID


class UserProfileService:
    
    @staticmethod
    def get_user_profile(user: User) -> dict:
        """Get current user profile"""
        user_profile = UserProfileOut.model_validate(user)
        return {
            "success": True,
            "data": user_profile,
            "message": "User profile retrieved successfully"
        }
    
    @staticmethod
    def update_user_profile(db: Session, user: User, profile_data: UserProfileUpdate) -> dict:
        """Update user profile"""
        update_data = profile_data.model_dump(exclude_unset=True)
        
        # Check if username is being changed and if it's unique
        if "username" in update_data and update_data["username"] != user.username:
            existing_user = db.query(User).filter(User.username == update_data["username"]).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
        
        # Update user fields
        for field, value in update_data.items():
            setattr(user, field, value)
        
        try:
            db.commit()
            db.refresh(user)
            
            user_profile = UserProfileOut.model_validate(user)
            return {
                "success": True,
                "data": user_profile,
                "message": "User profile updated successfully"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
    
    @staticmethod
    async def upload_user_avatar(db: Session, user: User, file: UploadFile) -> dict:
        """Upload user profile picture"""
        try:
            # Delete old profile picture if exists
            if user.profile_picture_url:
                delete_profile_picture(user.profile_picture_url)
            
            # Upload new profile picture
            file_path = await upload_profile_picture(file)
            
            # Update user profile picture URL
            user.profile_picture_url = file_path
            db.commit()
            db.refresh(user)
            
            user_profile = UserProfileOut.model_validate(user)
            return {
                "success": True,
                "data": user_profile,
                "message": "Profile picture uploaded successfully"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload profile picture: {str(e)}"
            )
    
    @staticmethod
    def remove_user_avatar(db: Session, user: User) -> dict:
        """Remove user profile picture"""
        try:
            # Delete profile picture file if exists
            if user.profile_picture_url:
                delete_profile_picture(user.profile_picture_url)
            
            # Remove profile picture URL from user
            user.profile_picture_url = None
            db.commit()
            db.refresh(user)
            
            return {
                "success": True,
                "message": "Profile picture removed successfully"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove profile picture"
            )
    
    @staticmethod
    def get_user_preferences(db: Session, user: User) -> dict:
        """Get user preferences"""
        preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        
        if not preferences:
            # Create default preferences if they don't exist
            preferences = UserPreferences(
                user_id=user.id,
                **UserPreferencesBase().model_dump()
            )
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
        
        preferences_out = UserPreferencesOut.model_validate(preferences)
        return {
            "success": True,
            "data": preferences_out,
            "message": "User preferences retrieved successfully"
        }
    
    @staticmethod
    def update_user_preferences(db: Session, user: User, preferences_data: UserPreferencesUpdate) -> dict:
        """Update user preferences"""
        preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        
        if not preferences:
            # Create new preferences if they don't exist
            preferences = UserPreferences(user_id=user.id)
            db.add(preferences)
        
        # Update preferences fields
        update_data = preferences_data.model_dump(exclude_unset=True)
        
        # Handle notification_settings JSON serialization
        if "notification_settings" in update_data and update_data["notification_settings"]:
            update_data["notification_settings"] = json.dumps(update_data["notification_settings"])
        
        for field, value in update_data.items():
            setattr(preferences, field, value)
        
        try:
            db.commit()
            db.refresh(preferences)
            
            preferences_out = UserPreferencesOut.model_validate(preferences)
            return {
                "success": True,
                "data": preferences_out,
                "message": "User preferences updated successfully"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user preferences"
            )
    
    @staticmethod
    def delete_user_account(db: Session, user: User) -> dict:
        """Delete user account and all associated data"""
        try:
            # Delete profile picture if exists
            if user.profile_picture_url:
                delete_profile_picture(user.profile_picture_url)
            
            # Delete user preferences
            preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
            if preferences:
                db.delete(preferences)
            
            # Delete user
            user_data = UserProfileOut.model_validate(user)
            db.delete(user)
            db.commit()
            
            return {
                "success": True,
                "data": user_data,
                "message": "User account deleted successfully"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user account"
            )
