from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from database import get_db
import models, schema, oauth2
from utils import verify_password


# we can use the "oauth2PasswordRequestForm" to get the username and password from the form data
# but i'm not gonna use it here to keep it simple

router = APIRouter(tags = ["Authentication"])

@router.post("/login", response_model=schema.Token)
async def login(user_credentials: schema.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
    
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}