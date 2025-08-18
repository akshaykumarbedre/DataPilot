"""
Authentication service for user login and session management.
"""
import logging
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from ..database.models import User
from ..database.database import db_manager

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Handles user authentication and session management."""
    
    def __init__(self):
        self.current_user: Optional[dict] = None  # Changed from User to dict
        self.session_start_time: Optional[datetime] = None
        self.failed_attempts = 0
        self.lockout_until: Optional[datetime] = None
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user with username and password.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Check if account is locked out
            if self.lockout_until and datetime.utcnow() < self.lockout_until:
                logger.warning(f"Login attempt during lockout for user: {username}")
                return False
            
            # Reset lockout if time has passed
            if self.lockout_until and datetime.utcnow() >= self.lockout_until:
                self.lockout_until = None
                self.failed_attempts = 0
            
            session = db_manager.get_session()
            try:
                # Find user by username
                user = session.query(User).filter(User.username == username).first()
                
                if user and self._verify_password(password, user.password_hash):
                    # Successful authentication
                    # Store user data instead of the SQLAlchemy object
                    self.current_user = {
                        'id': user.id,
                        'username': user.username,
                        'created_at': user.created_at,
                        'last_login': user.last_login
                    }
                    self.session_start_time = datetime.utcnow()
                    self.failed_attempts = 0
                    self.lockout_until = None
                    
                    # Update last login time
                    user.last_login = datetime.utcnow()
                    session.commit()
                    
                    logger.info(f"User {username} authenticated successfully")
                    return True
                else:
                    # Failed authentication
                    self.failed_attempts += 1
                    if self.failed_attempts >= 3:  # MAX_LOGIN_ATTEMPTS from config
                        self.lockout_until = datetime.utcnow() + timedelta(minutes=5)
                        logger.warning(f"Account locked for user: {username}")
                    
                    logger.warning(f"Authentication failed for user: {username}")
                    return False
                    
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def logout(self):
        """Log out the current user."""
        if self.current_user:
            logger.info(f"User {self.current_user['username']} logged out")
        
        self.current_user = None
        self.session_start_time = None
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_user is not None
    
    def is_session_valid(self) -> bool:
        """Check if the current session is still valid."""
        if not self.is_authenticated() or not self.session_start_time:
            return False
        
        # Check session timeout (1 hour)
        session_duration = datetime.utcnow() - self.session_start_time
        return session_duration.total_seconds() < 3600  # SESSION_TIMEOUT from config
    
    def get_current_user(self) -> Optional[dict]:
        """Get the currently authenticated user."""
        if self.is_session_valid():
            return self.current_user
        else:
            self.logout()
            return None
    
    def is_locked_out(self) -> bool:
        """Check if the account is currently locked out."""
        return self.lockout_until is not None and datetime.utcnow() < self.lockout_until
    
    def get_lockout_time_remaining(self) -> Optional[int]:
        """Get remaining lockout time in seconds."""
        if not self.is_locked_out():
            return None
        
        remaining = (self.lockout_until - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# Global authentication service instance
auth_service = AuthenticationService()
