from datetime import datetime
import re
from urllib.parse import quote


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    # Remove special characters except hyphens
    text = re.sub(r'[^\w\-]', '', text)
    # Replace multiple hyphens with single hyphen
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text


def truncate_text(text: str, max_length: int = 150, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


class ErrorResponse:
    """Standard error response format"""
    
    @staticmethod
    def error(message: str, status_code: int = 400, detail: str = None):
        """Generate error response"""
        return {
            "success": False,
            "message": message,
            "detail": detail,
            "status_code": status_code
        }


class SuccessResponse:
    """Standard success response format"""
    
    @staticmethod
    def success(data=None, message: str = "Success"):
        """Generate success response"""
        return {
            "success": True,
            "message": message,
            "data": data
        }
