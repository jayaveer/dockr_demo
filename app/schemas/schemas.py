from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8)


class UserSignIn(BaseModel):
    """Schema for user sign in"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_verified: bool
    date_added: datetime
    date_updated: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChangeRequest(BaseModel):
    """Schema for password change"""
    old_password: str
    new_password: str = Field(..., min_length=8)


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema for reset password"""
    token: str
    new_password: str = Field(..., min_length=8)


class TagBase(BaseModel):
    """Base tag schema"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)


class TagCreate(TagBase):
    """Schema for tag creation"""
    pass


class TagResponse(TagBase):
    """Schema for tag response"""
    id: int
    date_added: datetime
    date_updated: datetime
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for category creation"""
    pass


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    date_added: datetime
    date_updated: datetime
    
    class Config:
        from_attributes = True


class PostBase(BaseModel):
    """Base post schema"""
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    content: str
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    is_published: bool = False
    featured_image_url: Optional[str] = None
    tag_ids: list[int] = []


class PostCreate(PostBase):
    """Schema for post creation"""
    pass


class PostUpdate(BaseModel):
    """Schema for post update"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    is_published: Optional[bool] = None
    featured_image_url: Optional[str] = None
    tag_ids: Optional[list[int]] = None


class PostResponse(PostBase):
    """Schema for post response"""
    id: int
    author_id: int
    view_count: int
    published_at: Optional[datetime]
    date_added: datetime
    date_updated: datetime
    author: UserResponse
    category: Optional[CategoryResponse]
    tags: list[TagResponse]
    
    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    """Base comment schema"""
    content: str = Field(..., min_length=1)
    parent_comment_id: Optional[int] = None


class CommentCreate(CommentBase):
    """Schema for comment creation"""
    pass


class CommentUpdate(BaseModel):
    """Schema for comment update"""
    content: str = Field(..., min_length=1)


class CommentResponse(CommentBase):
    """Schema for comment response"""
    id: int
    post_id: int
    author_id: int
    is_approved: bool
    date_added: datetime
    date_updated: datetime
    author: UserResponse
    
    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    
    class Config:
        from_attributes = True
