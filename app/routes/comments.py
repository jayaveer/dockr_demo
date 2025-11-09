from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_token
from app.schemas.schemas import (
    CommentCreate, CommentUpdate, CommentResponse
)
from app.services.service import CommentService, PostService, UserService
from app.core.logging import logger

router = APIRouter(prefix="/api/v1/comments", tags=["Comments"])


def get_current_user(token_payload: dict = Depends(get_token), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    user_id = int(token_payload.get("sub"))
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/post/{post_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: int, comment_create: CommentCreate, 
                  current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a comment on a post"""
    try:
        # Check if post exists
        post = PostService.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        db_comment = CommentService.create_comment(db, comment_create, post_id, current_user.id)
        return CommentResponse.from_orm(db_comment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating comment"
        )


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Get a comment by ID"""
    db_comment = CommentService.get_comment_by_id(db, comment_id)
    
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return CommentResponse.from_orm(db_comment)


@router.get("/post/{post_id}", response_model=list[CommentResponse])
def get_post_comments(post_id: int, skip: int = Query(0, ge=0), 
                     limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Get all comments for a post"""
    # Check if post exists
    post = PostService.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = CommentService.get_post_comments(db, post_id, skip=skip, limit=limit)
    return [CommentResponse.from_orm(c) for c in comments]


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(comment_id: int, comment_update: CommentUpdate, 
                  current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a comment (author only)"""
    db_comment = CommentService.get_comment_by_id(db, comment_id)
    
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if db_comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    
    try:
        updated_comment = CommentService.update_comment(db, comment_id, comment_update, current_user.id)
        return CommentResponse.from_orm(updated_comment)
    except Exception as e:
        logger.error(f"Error updating comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating comment"
        )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, current_user = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """Delete a comment (author only)"""
    db_comment = CommentService.get_comment_by_id(db, comment_id)
    
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if db_comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    try:
        CommentService.delete_comment(db, comment_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting comment"
        )
