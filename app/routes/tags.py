from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_token
from app.schemas.schemas import TagCreate, TagResponse
from app.services.service import TagService, UserService
from app.core.logging import logger

router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])


def get_current_user(token_payload: dict = Depends(get_token), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    user_id = int(token_payload.get("sub"))
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag_create: TagCreate, current_user = Depends(get_current_user),
              db: Session = Depends(get_db)):
    """Create a new tag"""
    try:
        db_tag = TagService.create_tag(db, tag_create, current_user.id)
        return TagResponse.from_orm(db_tag)
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating tag"
        )


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """Get a tag by ID"""
    db_tag = TagService.get_tag_by_id(db, tag_id)
    
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    return TagResponse.from_orm(db_tag)


@router.get("", response_model=list[TagResponse])
def list_tags(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
             db: Session = Depends(get_db)):
    """List all tags"""
    tags = TagService.get_all_tags(db, skip=skip, limit=limit)
    return [TagResponse.from_orm(t) for t in tags]


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, current_user = Depends(get_current_user),
              db: Session = Depends(get_db)):
    """Delete a tag"""
    db_tag = TagService.get_tag_by_id(db, tag_id)
    
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    try:
        TagService.delete_tag(db, tag_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting tag"
        )
