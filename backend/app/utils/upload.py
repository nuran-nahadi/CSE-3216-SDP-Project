from fastapi import UploadFile, HTTPException
from typing import List
import os
import uuid
import shutil

# Create upload directories if they don't exist
UPLOAD_DIR = "uploads/products"
PROFILE_UPLOAD_DIR = "uploads/profiles"
RECEIPTS_UPLOAD_DIR = "uploads/receipts"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROFILE_UPLOAD_DIR, exist_ok=True)
os.makedirs(RECEIPTS_UPLOAD_DIR, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (this is approximate since we haven't read the whole file yet)
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")


async def upload_profile_picture(file: UploadFile) -> str:
    """Upload profile picture and return the file path"""
    validate_image(file)
    
    file_extension = file.filename.split(".")[-1].lower()
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(PROFILE_UPLOAD_DIR, file_name)
    
    # Save file to local directory
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return relative path that will be stored in database
    return f"/uploads/profiles/{file_name}"


def delete_profile_picture(file_path: str) -> bool:
    """Delete profile picture file"""
    if not file_path:
        return True
    
    # Convert relative path to absolute path
    if file_path.startswith("/uploads/profiles/"):
        file_name = file_path.split("/")[-1]
        absolute_path = os.path.join(PROFILE_UPLOAD_DIR, file_name)
        
        if os.path.exists(absolute_path):
            try:
                os.remove(absolute_path)
                return True
            except OSError:
                return False
    
    return True


async def upload_image(file: UploadFile) -> str:
    """Upload product image and return the file path"""
    validate_image(file)
    
    file_extension = file.filename.split(".")[-1].lower()
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Save file to local directory
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return relative path that will be stored in database
    return f"/uploads/products/{file_name}"


async def upload_multiple_images(files: List[UploadFile]) -> List[str]:
    urls = []
    for file in files:
        url = await upload_image(file)
        urls.append(url)

    # Return list relative paths that will be stored in database
    return urls


async def upload_receipt_image(file: UploadFile) -> str:
    """Upload receipt image and return the file path"""
    validate_image(file)
    
    file_extension = file.filename.split(".")[-1].lower()
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(RECEIPTS_UPLOAD_DIR, file_name)
    
    # Save file to local directory
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return relative path that will be stored in database
    return f"/uploads/receipts/{file_name}"


def delete_receipt_image(file_path: str) -> bool:
    """Delete receipt image file"""
    if not file_path:
        return True
    
    # Convert relative path to absolute path
    if file_path.startswith("/uploads/receipts/"):
        file_name = file_path.split("/")[-1]
        absolute_path = os.path.join(RECEIPTS_UPLOAD_DIR, file_name)
        
        if os.path.exists(absolute_path):
            try:
                os.remove(absolute_path)
                return True
            except OSError:
                return False
    
    return True