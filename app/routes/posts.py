from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_token
from app.schemas.schemas import (
    PostCreate, PostUpdate, PostResponse, PaginationParams
)
from app.services.service import PostService, UserService
from app.utils.helpers import SuccessResponse
from app.core.logging import logger

router = APIRouter(prefix="/api/v1/posts", tags=["Posts"])


def get_current_user(token_payload: dict = Depends(get_token), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    user_id = int(token_payload.get("sub"))
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post_create: PostCreate, current_user = Depends(get_current_user), 
               db: Session = Depends(get_db)):
    """Create a new post"""
    try:
        db_post = PostService.create_post(db, post_create, current_user.id)
        return PostResponse.from_orm(db_post)
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating post"
        )


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a post by ID"""
    db_post = PostService.get_post_by_id(db, post_id)
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    PostService.increment_view_count(db, post_id)
    
    return PostResponse.from_orm(db_post)


@router.get("", response_model=list[PostResponse])
def list_posts(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100),
              category_id: int = Query(None), tag_id: int = Query(None),
              db: Session = Depends(get_db)):
    """List all published posts with pagination and filtering"""
    posts = PostService.get_all_posts(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        tag_id=tag_id,
        published_only=True
    )
    return [PostResponse.from_orm(p) for p in posts]


@router.get("/search/{search_query}", response_model=list[PostResponse])
def search_posts(search_query: str, skip: int = Query(0, ge=0), 
                limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Search posts by title or content"""
    posts = PostService.search_posts(db, search_query, skip=skip, limit=limit)
    return [PostResponse.from_orm(p) for p in posts]


@router.get("/user/{user_id}", response_model=list[PostResponse])
def get_user_posts(user_id: int, skip: int = Query(0, ge=0), 
                  limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get all posts by a specific user"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    posts = PostService.get_user_posts(db, user_id, skip=skip, limit=limit)
    return [PostResponse.from_orm(p) for p in posts]


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_update: PostUpdate, current_user = Depends(get_current_user),
               db: Session = Depends(get_db)):
    """Update a post (author only)"""
    db_post = PostService.get_post_by_id(db, post_id)
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    try:
        updated_post = PostService.update_post(db, post_id, post_update, current_user.id)
        return PostResponse.from_orm(updated_post)
    except Exception as e:
        logger.error(f"Error updating post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating post"
        )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, current_user = Depends(get_current_user),
               db: Session = Depends(get_db)):
    """Delete a post (author only)"""
    db_post = PostService.get_post_by_id(db, post_id)
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    try:
        PostService.delete_post(db, post_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting post"
        )
