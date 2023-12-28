from sqlalchemy import ForeignKey, Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from src.db.database import Base


class Feed(Base):
    __tablename__ = "feed_action"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    user = relationship("User")
    post_id = Column(Integer, ForeignKey("post.id"), primary_key=True)
    post = relationship("Post")
    action = Column(String)
    time = Column(TIMESTAMP)