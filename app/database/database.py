"""
Database connection and setup utilities.
"""
import logging
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from .models import Base, User
from ..config import DATABASE_PATH
import bcrypt

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, database_path: Path = DATABASE_PATH):
        self.database_path = database_path
        self.engine = None
        self.SessionLocal = None
        
    def initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            # Create SQLite database connection
            self.engine = create_engine(
                f"sqlite:///{self.database_path}",
                echo=False,  # Set to True for SQL debugging
                connect_args={"check_same_thread": False}
            )
            
            # Enable foreign key constraints for SQLite
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create default admin user if none exists
            self._create_default_user()
            
            logger.info(f"Database initialized successfully at {self.database_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            return False
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        return self.SessionLocal()
    
    def _create_default_user(self):
        """Create default admin user if none exists."""
        try:
            session = self.get_session()
            
            # Check if any user exists
            existing_user = session.query(User).first()
            if existing_user:
                session.close()
                return
            
            # Create default admin user
            default_password = "a"
            password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
            
            admin_user = User(
                username="a",
                password_hash=password_hash.decode('utf-8')
            )
            
            session.add(admin_user)
            session.commit()
            session.close()
            
            logger.info("Default admin user created (username: Dr Yashoda, password: yashoda123)")
            
        except Exception as e:
            logger.error(f"Failed to create default user: {str(e)}")
    
    def backup_database(self, backup_path: Path):
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.database_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup database: {str(e)}")
            return False
    
    def get_database_path(self) -> str:
        """Get the database file path."""
        return str(self.database_path)
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()
