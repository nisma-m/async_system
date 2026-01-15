from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from app.dependencies import admin_required
from app.database import users_collection
from app.schemas import ProfileSchema
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

# =============================
# Schema for Admin Update
# =============================
class AdminUpdateSchema(BaseModel):
    profile: Optional[ProfileSchema] = None
    role: Optional[str] = None  # Admin can promote/demote users

# =============================
# List All Users (with pagination & filter)
# =============================
@router.get("/users")
async def list_users(admin=Depends(admin_required)):
    users_cursor = users_collection.find({}, {"password": 0})
    users = []
    async for user in users_cursor:
        # Convert ObjectId to str
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

# @router.get("/users")
# async def list_users(
#     skip: int = 0,
#     limit: int = 50,
#     role: Optional[str] = Query(None),
#     email: Optional[str] = Query(None),
#     admin=Depends(admin_required)
# ):
#     """
#     List all users. Admin only.
#     Supports optional filters: role & email.
#     Supports pagination with skip & limit.
#     """
#     query = {}
#     if role:
#         query["role"] = role
#     if email:
#         query["email"] = {"$regex": email, "$options": "i"}

#     users_cursor = users_collection.find(query, {"password": 0}).skip(skip).limit(limit)
#     users = []
#     async for user in users_cursor:
#         users.append(user)
#     return users

# =============================
# Update User Profile or Role
# =============================
@router.put("/users/{user_email}")
async def update_user_profile(
    user_email: str,
    data: AdminUpdateSchema,
    admin=Depends(admin_required)
):
    """
    Update any user's profile and/or role.
    """
    update_data = {}
    if data.profile:
        update_data["profile"] = data.profile.dict(exclude_unset=True)
    if data.role:
        if data.role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")
        update_data["role"] = data.role
    if not update_data:
        raise HTTPException(status_code=400, detail="Nothing to update")

    result = await users_collection.update_one(
        {"email": user_email},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

# =============================
# Delete User
# =============================
@router.delete("/users/{user_email}")
async def delete_user(
    user_email: str,
    admin=Depends(admin_required)
):

    if user_email == admin["email"]:
        raise HTTPException(status_code=400, detail="Admin cannot delete themselves")

    result = await users_collection.delete_one({"email": user_email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
