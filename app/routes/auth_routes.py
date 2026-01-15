from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas import RegisterSchema, LoginResponse
from app.database import users_collection, token_blacklist_collection
from app.auth import hash_password, verify_password, create_access_token
from app.database import token_blacklist_collection
from app.dependencies import security


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(user: RegisterSchema):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    await users_collection.insert_one({
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role,
        "last_login": None,
        "profile": {}
    })
    return {"message": "User registered successfully"}

@router.post("/login", response_model=LoginResponse)
async def login(user: RegisterSchema):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last login timestamp
    await users_collection.update_one(
        {"email": user.email},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    token = create_access_token({"email": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Add token to blacklist
    await token_blacklist_collection.insert_one({"token": token})
    return {"message": "Successfully logged out"}