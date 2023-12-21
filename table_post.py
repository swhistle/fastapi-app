from sqlalchemy import Column, Integer, String
from database import Base, SessionLocal

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)


if __name__ == "__main__":
    session = SessionLocal()

    post_list = []

    for post in (
        session.query(Post)
        .filter(Post.topic == 'business')
        .order_by(Post.id.desc())
        .limit(10)
        .all()
    ):
        post_list.append(post.id)

    print(post_list)