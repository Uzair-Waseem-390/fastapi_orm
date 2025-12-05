from fastapi import FastAPI
import models
from database import engine
from routes import post, user, auth
from routes import like
from fastapi.middleware.cors import CORSMiddleware

# Create tables
models.Base.metadata.create_all(bind=engine)

origin = ["*"]

# Initialize FastAPI
app = FastAPI(title="FastAPI App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(like.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}
