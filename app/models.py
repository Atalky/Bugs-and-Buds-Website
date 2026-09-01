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