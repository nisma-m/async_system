from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.database import users_collection, token_blacklist_collection

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    blacklisted = await token_blacklist_collection.find_one({"token": token})
    if blacklisted:
        raise HTTPException(status_code=401, detail="Token has been revoked (logged out)")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Role-based access
async def admin_required(current_user_email: str = Depends(get_current_user)):
    user = await users_collection.find_one({"email": current_user_email})
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
