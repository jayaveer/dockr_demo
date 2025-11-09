from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.models import User, Post, Comment, Category, Tag
from app.schemas.schemas import (
    UserCreate, PostCreate, PostUpdate, CommentCreate, CommentUpdate,
    CategoryCreate, TagCreate
)
from app.core.security import hash_password, verify_password
from app.utils.helpers import generate_slug
from app.core.logging import logger
from datetime import datetime


class UserService:
    """Service for user operations"""
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create a new user"""
        try:
            db_user = User(
                email=user_create.email,
                username=user_create.username,
                full_name=user_create.full_name,
                hashed_password=hash_password(user_create.password),
                bio=user_create.bio,
                profile_image_url=user_create.profile_image_url
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"User created: {db_user.email}")
            return db_user
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """Get user by email"""
        return db.query(User).filter(
            and_(User.email == email, User.deleted_at == None)
        ).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """Get user by username"""
        return db.query(User).filter(
            and_(User.username == username, User.deleted_at == None)
        ).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID"""
        return db.query(User).filter(
            and_(User.id == user_id, User.deleted_at == None)
        ).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        user = UserService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str) -> bool:
        """Update user password"""
        try:
            user = UserService.get_user_by_id(db, user_id)
            if not user:
                return False
            user.hashed_password = hash_password(new_password)
            user.updated_by = user_id
            user.date_updated = datetime.utcnow()
            db.commit()
            logger.info(f"Password updated for user: {user.email}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating password: {str(e)}")
            raise
    
    @staticmethod
    def verify_user_email(db: Session, user_id: int) -> bool:
        """Mark user email as verified"""
        try:
            user = UserService.get_user_by_id(db, user_id)
            if not user:
                return False
            user.is_verified = True
            user.updated_by = user_id
            user.date_updated = datetime.utcnow()
            db.commit()
            logger.info(f"Email verified for user: {user.email}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error verifying email: {str(e)}")
            raise


class CategoryService:
    """Service for category operations"""
    
    @staticmethod
    def create_category(db: Session, category_create: CategoryCreate, user_id: int) -> Category:
        """Create a new category"""
        try:
            db_category = Category(
                name=category_create.name,
                slug=generate_slug(category_create.slug),
                description=category_create.description,
                added_by=user_id,
                updated_by=user_id
            )
            db.add(db_category)
            db.commit()
            db.refresh(db_category)
            logger.info(f"Category created: {db_category.name}")
            return db_category
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating category: {str(e)}")
            raise
    
    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Category:
        """Get category by ID"""
        return db.query(Category).filter(
            and_(Category.id == category_id, Category.deleted_at == None)
        ).first()
    
    @staticmethod
    def get_all_categories(db: Session, skip: int = 0, limit: int = 100):
        """Get all categories"""
        return db.query(Category).filter(
            Category.deleted_at == None
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_category(db: Session, category_id: int, user_id: int) -> bool:
        """Soft delete a category"""
        try:
            category = CategoryService.get_category_by_id(db, category_id)
            if not category:
                return False
            category.deleted_at = datetime.utcnow()
            category.updated_by = user_id
            db.commit()
            logger.info(f"Category deleted: {category.name}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting category: {str(e)}")
            raise


class TagService:
    """Service for tag operations"""
    
    @staticmethod
    def create_tag(db: Session, tag_create: TagCreate, user_id: int) -> Tag:
        """Create a new tag"""
        try:
            db_tag = Tag(
                name=tag_create.name,
                slug=generate_slug(tag_create.slug),
                added_by=user_id,
                updated_by=user_id
            )
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
            logger.info(f"Tag created: {db_tag.name}")
            return db_tag
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating tag: {str(e)}")
            raise
    
    @staticmethod
    def get_tag_by_id(db: Session, tag_id: int) -> Tag:
        """Get tag by ID"""
        return db.query(Tag).filter(
            and_(Tag.id == tag_id, Tag.deleted_at == None)
        ).first()
    
    @staticmethod
    def get_all_tags(db: Session, skip: int = 0, limit: int = 100):
        """Get all tags"""
        return db.query(Tag).filter(
            Tag.deleted_at == None
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_tag(db: Session, tag_id: int, user_id: int) -> bool:
        """Soft delete a tag"""
        try:
            tag = TagService.get_tag_by_id(db, tag_id)
            if not tag:
                return False
            tag.deleted_at = datetime.utcnow()
            tag.updated_by = user_id
            db.commit()
            logger.info(f"Tag deleted: {tag.name}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting tag: {str(e)}")
            raise


class PostService:
    """Service for post operations"""
    
    @staticmethod
    def create_post(db: Session, post_create: PostCreate, user_id: int) -> Post:
        """Create a new post"""
        try:
            db_post = Post(
                title=post_create.title,
                slug=generate_slug(post_create.slug),
                content=post_create.content,
                excerpt=post_create.excerpt,
                author_id=user_id,
                category_id=post_create.category_id,
                is_published=post_create.is_published,
                featured_image_url=post_create.featured_image_url,
                added_by=user_id,
                updated_by=user_id
            )
            
            # Add tags
            if post_create.tag_ids:
                tags = db.query(Tag).filter(Tag.id.in_(post_create.tag_ids)).all()
                db_post.tags = tags
            
            db.add(db_post)
            db.commit()
            db.refresh(db_post)
            logger.info(f"Post created: {db_post.title}")
            return db_post
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating post: {str(e)}")
            raise
    
    @staticmethod
    def get_post_by_id(db: Session, post_id: int) -> Post:
        """Get post by ID"""
        return db.query(Post).filter(
            and_(Post.id == post_id, Post.deleted_at == None)
        ).first()
    
    @staticmethod
    def get_post_by_slug(db: Session, slug: str) -> Post:
        """Get post by slug"""
        return db.query(Post).filter(
            and_(Post.slug == slug, Post.deleted_at == None)
        ).first()
    
    @staticmethod
    def get_all_posts(db: Session, skip: int = 0, limit: int = 10, 
                     category_id: int = None, tag_id: int = None,
                     published_only: bool = True):
        """Get all posts with filtering"""
        query = db.query(Post).filter(Post.deleted_at == None)
        
        if published_only:
            query = query.filter(Post.is_published == True)
        
        if category_id:
            query = query.filter(Post.category_id == category_id)
        
        if tag_id:
            query = query.join(Post.tags).filter(Tag.id == tag_id)
        
        return query.order_by(Post.date_added.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def search_posts(db: Session, search_query: str, skip: int = 0, limit: int = 10):
        """Search posts by title or content"""
        return db.query(Post).filter(
            and_(
                Post.deleted_at == None,
                Post.is_published == True,
                or_(
                    Post.title.ilike(f"%{search_query}%"),
                    Post.content.ilike(f"%{search_query}%"),
                    Post.excerpt.ilike(f"%{search_query}%")
                )
            )
        ).order_by(Post.date_added.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_posts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
        """Get all posts by a user"""
        return db.query(Post).filter(
            and_(Post.author_id == user_id, Post.deleted_at == None)
        ).order_by(Post.date_added.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_post(db: Session, post_id: int, post_update: PostUpdate, user_id: int) -> Post:
        """Update a post"""
        try:
            db_post = PostService.get_post_by_id(db, post_id)
            if not db_post:
                return None
            
            if post_update.title:
                db_post.title = post_update.title
            if post_update.slug:
                db_post.slug = generate_slug(post_update.slug)
            if post_update.content:
                db_post.content = post_update.content
            if post_update.excerpt is not None:
                db_post.excerpt = post_update.excerpt
            if post_update.category_id is not None:
                db_post.category_id = post_update.category_id
            if post_update.is_published is not None:
                db_post.is_published = post_update.is_published
            if post_update.featured_image_url is not None:
                db_post.featured_image_url = post_update.featured_image_url
            if post_update.tag_ids is not None:
                tags = db.query(Tag).filter(Tag.id.in_(post_update.tag_ids)).all()
                db_post.tags = tags
            
            db_post.updated_by = user_id
            db_post.date_updated = datetime.utcnow()
            db.commit()
            db.refresh(db_post)
            logger.info(f"Post updated: {db_post.title}")
            return db_post
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating post: {str(e)}")
            raise
    
    @staticmethod
    def delete_post(db: Session, post_id: int, user_id: int) -> bool:
        """Soft delete a post"""
        try:
            db_post = PostService.get_post_by_id(db, post_id)
            if not db_post:
                return False
            db_post.deleted_at = datetime.utcnow()
            db_post.updated_by = user_id
            db.commit()
            logger.info(f"Post deleted: {db_post.title}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting post: {str(e)}")
            raise
    
    @staticmethod
    def increment_view_count(db: Session, post_id: int):
        """Increment post view count"""
        try:
            db_post = PostService.get_post_by_id(db, post_id)
            if db_post:
                db_post.view_count += 1
                db.commit()
        except Exception as e:
            logger.error(f"Error incrementing view count: {str(e)}")


class CommentService:
    """Service for comment operations"""
    
    @staticmethod
    def create_comment(db: Session, comment_create: CommentCreate, post_id: int, user_id: int) -> Comment:
        """Create a new comment"""
        try:
            db_comment = Comment(
                content=comment_create.content,
                post_id=post_id,
                author_id=user_id,
                parent_comment_id=comment_create.parent_comment_id,
                added_by=user_id,
                updated_by=user_id
            )
            db.add(db_comment)
            db.commit()
            db.refresh(db_comment)
            logger.info(f"Comment created on post {post_id}")
            return db_comment
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating comment: {str(e)}")
            raise
    
    @staticmethod
    def get_comment_by_id(db: Session, comment_id: int) -> Comment:
        """Get comment by ID"""
        return db.query(Comment).filter(
            and_(Comment.id == comment_id, Comment.deleted_at == None)
        ).first()
    
    @staticmethod
    def get_post_comments(db: Session, post_id: int, skip: int = 0, limit: int = 20, approved_only: bool = True):
        """Get all comments for a post"""
        query = db.query(Comment).filter(
            and_(Comment.post_id == post_id, Comment.deleted_at == None)
        )
        
        if approved_only:
            query = query.filter(Comment.is_approved == True)
        
        return query.order_by(Comment.date_added.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_comment(db: Session, comment_id: int, comment_update: CommentUpdate, user_id: int) -> Comment:
        """Update a comment"""
        try:
            db_comment = CommentService.get_comment_by_id(db, comment_id)
            if not db_comment:
                return None
            db_comment.content = comment_update.content
            db_comment.updated_by = user_id
            db_comment.date_updated = datetime.utcnow()
            db.commit()
            db.refresh(db_comment)
            logger.info(f"Comment updated: {comment_id}")
            return db_comment
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating comment: {str(e)}")
            raise
    
    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
        """Soft delete a comment"""
        try:
            db_comment = CommentService.get_comment_by_id(db, comment_id)
            if not db_comment:
                return False
            db_comment.deleted_at = datetime.utcnow()
            db_comment.updated_by = user_id
            db.commit()
            logger.info(f"Comment deleted: {comment_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting comment: {str(e)}")
            raise
    
    @staticmethod
    def approve_comment(db: Session, comment_id: int, user_id: int) -> bool:
        """Approve a comment"""
        try:
            db_comment = CommentService.get_comment_by_id(db, comment_id)
            if not db_comment:
                return False
            db_comment.is_approved = True
            db_comment.updated_by = user_id
            db.commit()
            logger.info(f"Comment approved: {comment_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error approving comment: {str(e)}")
            raise
