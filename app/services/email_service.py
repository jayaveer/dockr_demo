import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings
from app.core.logging import logger
import os


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        
        # Setup Jinja2 environment for email templates
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'templates',
            'emails'
        )
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def _render_template(self, template_name: str, context: dict) -> str:
        """Render email template with context"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            return None
    
    def send_email(self, recipient: str, subject: str, html_content: str) -> bool:
        """Send email to recipient"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False
    
    def send_verification_email(self, recipient: str, username: str, verification_token: str) -> bool:
        """Send email verification email"""
        verification_link = f"{settings.APP_NAME}/verify-email?token={verification_token}"
        
        html_content = self._render_template(
            'verification.html',
            {
                'username': username,
                'verification_link': verification_link,
                'app_name': settings.APP_NAME
            }
        )
        
        if html_content:
            return self.send_email(
                recipient,
                f"Email Verification - {settings.APP_NAME}",
                html_content
            )
        return False
    
    def send_password_reset_email(self, recipient: str, username: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_link = f"{settings.APP_NAME}/reset-password?token={reset_token}"
        
        html_content = self._render_template(
            'password_reset.html',
            {
                'username': username,
                'reset_link': reset_link,
                'app_name': settings.APP_NAME
            }
        )
        
        if html_content:
            return self.send_email(
                recipient,
                f"Password Reset - {settings.APP_NAME}",
                html_content
            )
        return False
    
    def send_welcome_email(self, recipient: str, username: str) -> bool:
        """Send welcome email"""
        html_content = self._render_template(
            'welcome.html',
            {
                'username': username,
                'app_name': settings.APP_NAME
            }
        )
        
        if html_content:
            return self.send_email(
                recipient,
                f"Welcome to {settings.APP_NAME}",
                html_content
            )
        return False


email_service = EmailService()
