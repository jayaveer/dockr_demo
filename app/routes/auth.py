from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import (
    create_access_token, get_token, create_password_reset_token,
    verify_password_reset_token, verify_password
)
from app.core.config import settings
from app.schemas.schemas import (
    UserCreate, UserSignIn, TokenResponse, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest, PasswordChangeRequest
)
from app.services.service import UserService
from app.services.email_service import email_service
from app.utils.helpers import ErrorResponse, SuccessResponse
from app.core.logging import logger

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = UserService.get_user_by_username(db, user_create.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        db_user = UserService.create_user(db, user_create)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.id)},
            expires_delta=access_token_expires
        )
        
        # Send welcome email
        email_service.send_welcome_email(db_user.email, db_user.username)
        
        logger.info(f"User registered successfully: {db_user.email}")
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(db_user)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during registration"
        )


@router.post("/signin", response_model=TokenResponse)
def signin(user_signin: UserSignIn, db: Session = Depends(get_db)):
    """Sign in user with email and password"""
    try:
        # Authenticate user
        db_user = UserService.authenticate_user(db, user_signin.email, user_signin.password)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.id)},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User signed in: {db_user.email}")
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(db_user)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during sign in"
        )


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    try:
        db_user = UserService.get_user_by_email(db, request.email)
        
        # Always return success for security (don't reveal if email exists)
        if db_user:
            reset_token = create_password_reset_token({"sub": str(db_user.id)})
            email_service.send_password_reset_email(db_user.email, db_user.username, reset_token)
            logger.info(f"Password reset email sent to: {db_user.email}")
        else:
            logger.warning(f"Password reset requested for non-existent email: {request.email}")
        
        return SuccessResponse(
            message="If the email exists, a password reset link has been sent"
        )
    
    except Exception as e:
        logger.error(f"Error during forgot password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing request"
        )


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with token"""
    try:
        # Verify token
        payload = verify_password_reset_token(request.token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        user_id = int(payload.get("sub"))
        db_user = UserService.get_user_by_id(db, user_id)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        UserService.update_password(db, user_id, request.new_password)
        
        logger.info(f"Password reset successfully for user: {db_user.email}")
        
        return SuccessResponse(message="Password reset successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error resetting password"
        )


def get_current_user_from_token(token_payload: dict = Depends(get_token), db: Session = Depends(get_db)):
    """Extract current user from token payload"""
    user_id = int(token_payload.get("sub"))
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/change-password")
def change_password(request: PasswordChangeRequest, 
                   current_user = Depends(get_current_user_from_token), 
                   db: Session = Depends(get_db)):
    """Change password for authenticated user"""
    try:
        user_id = current_user.id
        db_user = UserService.get_user_by_id(db, user_id)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify old password
        if not verify_password(request.old_password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Update password
        UserService.update_password(db, user_id, request.new_password)
        
        logger.info(f"Password changed for user: {db_user.email}")
        
        return SuccessResponse(message="Password changed successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error changing password"
        )
