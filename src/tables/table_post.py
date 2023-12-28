from sqlalchemy import Column, Integer, String
from src.db.database import Base

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)