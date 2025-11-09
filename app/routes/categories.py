from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_token
from app.schemas.schemas import CategoryCreate, CategoryResponse
from app.services.service import CategoryService, UserService
from app.core.logging import logger

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


def get_current_user(token_payload: dict = Depends(get_token), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    user_id = int(token_payload.get("sub"))
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_create: CategoryCreate, current_user = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """Create a new category"""
    try:
        db_category = CategoryService.create_category(db, category_create, current_user.id)
        return CategoryResponse.from_orm(db_category)
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating category"
        )


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a category by ID"""
    db_category = CategoryService.get_category_by_id(db, category_id)
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return CategoryResponse.from_orm(db_category)


@router.get("", response_model=list[CategoryResponse])
def list_categories(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
                   db: Session = Depends(get_db)):
    """List all categories"""
    categories = CategoryService.get_all_categories(db, skip=skip, limit=limit)
    return [CategoryResponse.from_orm(c) for c in categories]


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, current_user = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """Delete a category"""
    db_category = CategoryService.get_category_by_id(db, category_id)
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    try:
        CategoryService.delete_category(db, category_id, current_user.id)
    except Exception as e:
        logger.error(f"Error deleting category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting category"
        )
