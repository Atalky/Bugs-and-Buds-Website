from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False) #unique so no duplicate usernames
    hashed_password = Column(String, nullable=False) #store the hash, never the raw password
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    biography = Column(String, nullable=True) # Plain text.
    is_admin = Column(Boolean, server_default="false", nullable=False)
    projects = relationship("Project", back_populates="owner")
    posts = relationship("Post", back_populates="author")
    
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)  # for clean URLs like /projects/sudo-agent
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="projects")
    posts = relationship("Post", back_populates="project")
    
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True) #index=True -- not needed but here for clarity
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_posted = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    published = Column(Boolean, server_default="true", nullable=False)
    on_main_devlog = Column(Boolean, server_default="false", nullable=False)

    author = relationship("User", back_populates="posts")
    project = relationship("Project", back_populates="posts")


class Follow(Base):
    """One user following another. status stays "pending" until accepted when the followed user approves followers."""

    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    followed_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    status = Column(String, server_default="accepted", nullable=False)  # "pending" | "accepted"
    followed_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

