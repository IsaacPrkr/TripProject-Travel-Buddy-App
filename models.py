from sqlalchemy import Column, String
from database import Base

# Define User model for SQLAlchemy ORM
class UserDB(Base):
    __tablename__ = "users"

    userID = Column(String, primary_key=True, index=True)  # Unique user identifier
    name = Column(String, unique=True, index=True)
    password = Column(String)  
