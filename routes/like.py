from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schema, oauth2
from sqlalchemy import func

router = APIRouter(
    prefix="/likes",
    tags=["Likes"]
)


@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    # 1. Check if the post exists
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post does not exist"
        )

    # 2. Check if user already liked this post
    like_query = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    )
    existing_like = like_query.first()

    # 3. Toggle-like system (Like/Unlike)
    if existing_like:
        # User already liked → UNLIKE
        like_query.delete()
        db.commit()
        return {"message": "Post unliked successfully 👎"}

    # 4. Otherwise → LIKE the post
    new_like = models.Like(
        post_id=post_id,
        user_id=current_user.id
    )
    db.add(new_like)
    db.commit()
    return {"message": "Post liked successfully 👍"}



# @router.post("/", status_code=status.HTTP_201_CREATED)
# def like_post(
#     like: schema.LikeRequest,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(oauth2.get_current_user)
# ):
#     post = db.query(models.Post).filter(models.Post.id == like.post_id).first()

#     if not post:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Post does not exist"
#         )

#     like_query = db.query(models.Like).filter(
#         models.Like.post_id == like.post_id,
#         models.Llike.user_id == current_user.id
#     )

#     found_like = like_query.first()

#     if like.direction == 1:  # LIKE
#         if found_like:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="You have already liked this post"
#             )

#         new_like = models.Like(post_id=like.post_id, user_id=current_user.id)
#         db.add(new_like)
#         db.commit()
#         return {"message": "Post liked"}

#     else:  # UNLIKE (direction = 0)
#         if not found_like:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="You haven't liked this post yet"
#             )

#         like_query.delete()
#         db.commit()
#         return {"message": "Post unliked"}


@router.get("/user/{user_id}")
def get_posts_liked_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Only allow the logged-in user to see their own liked posts
    
    
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view likes of another user"
        )

    liked_posts = (
        db.query(models.Post)
        .join(models.Like, models.Post.id == models.Like.post_id)
        .filter(models.Like.user_id == user_id)
        .all()
    )

    return liked_posts


@router.get("/top/post")
def get_top_liked_posts(
    db: Session = Depends(get_db)
):

    posts = (
        db.query(
            models.Post,
            func.count(models.Like.post_id).label("likes_count")
        )
        .outerjoin(models.Like, models.Like.post_id == models.Post.id)
        .group_by(models.Post.id)
        .order_by(func.count(models.Like.post_id).desc())
        .all()
    )

    response = []
    for post, likes_count in posts:
        response.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id,
            "created_at": post.created_at,
            "likes": likes_count
        })

    return response
