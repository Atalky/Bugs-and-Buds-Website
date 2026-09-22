from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True) #index=True -- not needed but here for clarity
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author = Column(String, nullable=False)
    date_posted = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    published = Column(Boolean, server_default="true", nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False) #unique so no duplicate usernames
    hashed_password = Column(String, nullable=False) #store the hash, never the raw password
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    biography = Column(String, nullable=True) # Plain text.
    is_admin = Column(Boolean, server_default="false", nullable=False)
    