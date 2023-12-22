from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from table_post import Post
from table_user import User
from table_feed import Feed
from schema import UserGet, PostGet, FeedGet

def get_db():
    with SessionLocal() as db:
        return db

app = FastAPI()

@app.get("/")
def root() -> str:
    return 'root'

@app.get('/user/all', response_model=List[UserGet])
def get_all_users(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(User).limit(limit).all()

@app.get('/user/{id}', response_model=UserGet)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == int(id)).all()

    if not user:
        raise HTTPException(404, detail='user not found')

    return user[0]

@app.get('/user/{id}/feed', response_model=List[FeedGet])
def get_feed_by_user_id(id: int, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Feed).filter(Feed.user_id == int(id)).order_by(Feed.time.desc()).limit(limit).all()

@app.get('/post/all', response_model=List[PostGet])
def get_all_posts(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Post).limit(limit).all()

@app.get('/post/{id}', response_model=PostGet)
def get_post_by_id(id: int, db: Session=Depends(get_db)):
    post = db.query(Post.id, Post.text, Post.topic).filter(Post.id == int(id)).all()

    if not post:
        raise HTTPException(404, detail='post not found')

    return post[0]

@app.get('/post/{id}/feed', response_model=List[FeedGet])
def get_feed_by_post_id(id: int, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Feed).filter(Feed.post_id == int(id)).order_by(Feed.time.desc()).limit(limit).all()

@app.get('/post/recommendations/', response_model=List[PostGet])
def get_recommendations(id: int, limit: int = 10, db: Session = Depends(get_db)):
    return db\
        .query(Post)\
        .join(Feed, Post.id == Feed.post_id)\
        .filter(Feed.action == 'like')\
        .group_by(Post.id)\
        .order_by(func.count(Feed.action).desc())\
        .limit(limit)\
        .all()