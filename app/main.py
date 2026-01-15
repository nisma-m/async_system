from fastapi import FastAPI
from app.routes import auth_routes, user_routes, admin_routes

app = FastAPI(title="Async FastAPI Auth System")

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(admin_routes.router)

@app.get("/")
async def root():
    return {"message": "FastAPI Async Auth Backend Running"}
