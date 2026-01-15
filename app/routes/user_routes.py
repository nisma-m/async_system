from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from app.schemas import ProfileSchema
from app.database import users_collection
from app.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User Profile"])

@router.get("/profile")
async def get_profile(email: str = Depends(get_current_user)):
    user = await users_collection.find_one(
        {"email": email},
        {"_id": 0, "password": 0}
    )
    return user

@router.put("/profile")
async def update_profile(
    profile: ProfileSchema,
    email: str = Depends(get_current_user)
):
    await users_collection.update_one(
        {"email": email},
        {"$set": {"profile": profile.dict(exclude_unset=True)}}
    )
    return {"message": "Profile updated successfully"}


@router.post("/upload-avatar")
async def upload_avatar(file: UploadFile = File(...), current_user_email: str = Depends(get_current_user)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG allowed")

    file_location = f"avatars/{current_user_email}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Update avatar field in MongoDB
    await users_collection.update_one(
        {"email": current_user_email},
        {"$set": {"profile.avatar": file_location}}
    )
    return {"message": "Avatar uploaded successfully", "avatar_path": file_location}