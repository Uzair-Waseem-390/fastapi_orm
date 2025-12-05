from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schema, oauth2
from typing import Optional


router = APIRouter(tags = ["Posts"])


@router.post("/createpost/", status_code=status.HTTP_201_CREATED, response_model=schema.PostResponse)
async def create_post(post: schema.PostCreate,
                      db: Session = Depends(get_db),
                    #   current_user: schema.TokenData = Depends(oauth2.get_current_user)
                      current_user: models.User = Depends(oauth2.get_current_user)  # This gives you the actual user object
                      ):
    print(current_user.id)
    
    # Assign the current user's ID to the post
    new_post = models.Post(**post.dict(), user_id=current_user.id)
    # new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# @app.post("/createpost/")
# async def create_post(post: PostCreate, db: Session = Depends(get_db)):
#     new_post = models.Post(
#         title=post.title,
#         content=post.content,
#         published=post.published
#     )
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)
#     return {"message": "Post created", "content": new_post}


@router.get("/posts/", response_model=list[schema.PostResponse])
def get_posts(db: Session = Depends(get_db), 
              current_user: schema.TokenData = Depends(oauth2.get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""):
    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.get("/post/{id}", response_model=schema.PostResponse)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: schema.TokenData = Depends(oauth2.get_current_user)
             ):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this post")
    return post


@router.put("/post/{id}", status_code=status.HTTP_200_OK)
def update_post(id: int,
                updated_post: schema.PostUpdate,
                db: Session = Depends(get_db),
                current_user: schema.TokenData = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this post")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return {"message": "Post updated", "post": post_query.first()}


@router.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,
                db: Session = Depends(get_db),
                current_user: schema.TokenData = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
        
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this post")
    post_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "Post deleted"}


@router.post("/createpostid/{id}", status_code=status.HTTP_201_CREATED)
async def create_post_with_id(id: int,
                              post: schema.PostCreate,
                              db: Session = Depends(get_db),
                              current_user: schema.TokenData = Depends(oauth2.get_current_user)):
    existing_post = db.query(models.Post).filter(models.Post.id == id).first()
    if existing_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"Post with id {id} already exists")
    new_post = models.Post(id=id, **post.dict(), user_id=current_user.id)
    if new_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to create post with this ID")
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": "Post created with specified ID", "content": new_post}

@router.get("/post/{id}/likes")
def get_like_count(id: int, db: Session = Depends(get_db)):
    count = db.query(models.Like).filter(models.Like.post_id == id).count()
    return {"post_id": id, "likes": count}