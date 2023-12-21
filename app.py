import datetime
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from table_post import Post
from table_user import User
from schema import UserGet, PostGet

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
def user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == int(id)).all()

    if not user:
        raise HTTPException(404, detail='user not found')

    return user[0]

@app.get('/post/all', response_model=List[PostGet])
def get_all_users(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Post).limit(limit).all()
@app.get('/post/{id}', response_model=PostGet)
def user(id: int, db: Session=Depends(get_db)):
    post = db.query(Post.id, Post.text, Post.topic).filter(Post.id == int(id)).all()

    if not post:
        raise HTTPException(404, detail='post not found')

    return post[0]
