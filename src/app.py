import os
from catboost import CatBoostClassifier

from fastapi import Depends, FastAPI, HTTPException
from datetime import datetime
from sqlalchemy import func, create_engine
from sqlalchemy.orm import Session
import pandas as pd
from typing import List
import yaml
import uvicorn

from internals.db_connection.connection import connection_url

from src.db.database import SessionLocal
from src.tables.table_post import Post
from src.tables.table_user import User
from src.tables.table_feed import Feed
from src.schema.schema import UserGet, PostGet, FeedGet

def config():
    with open('config.yaml', 'r') as config_file:
        return yaml.safe_load(config_file)

def get_db():
    with SessionLocal() as db:
        return db

#Загрузка модели
def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально.
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH

def load_models():
    model_path = get_model_path("src/catBoost_classifier")
    model = CatBoostClassifier()
    model.load_model(fname=model_path)
    return model

def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 200000
    engine = create_engine(connection_url)
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)

def load_features() -> pd.DataFrame:
    query = """ SELECT * FROM "al-svistunov_users_features_lesson_22" """
    return batch_load_sql(query)


def load_posts_features() -> pd.DataFrame:
    query = """ SELECT * FROM "al-svistunov_posts_features_lesson_22" """
    return batch_load_sql(query)


def load_posts_content() -> pd.DataFrame:
    query = """ SELECT * FROM public.post_text_df """

    return batch_load_sql(query)


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
def get_feed_by_user_id(id: int, limit: int = 10, db: Session = Depends(get_db), config: dict = Depends(config)):
    return db.query(Feed).filter(Feed.user_id == int(id)).filter(Feed.time >= config['feed_start_date']).order_by(Feed.time.desc()).limit(limit).all()

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
def get_recommendations(id: int, time: datetime, limit: int = 10):
    df_recommendations = pd.DataFrame()

    user_id = id

    df_users_item = users_features[users_features['user_id'] == user_id]

    if df_users_item.empty:
        return []

    df_users_item = df_users_item.iloc[0]

    df_users_item['month'] = time.month
    df_users_item['dayofweek'] = time.weekday()
    df_users_item['hour'] = time.hour

    # Объединение датафреймов с данными пользователя и постов
    data_merged = posts_features.assign(**df_users_item)

    df_preds = data_merged.drop('user_id', axis=1)

    df_preds['prediction_proba'] = model.predict_proba(df_preds)[:, 1]
    df_preds.sort_values('prediction_proba', ascending=False, inplace=True)
    df_preds['user_id'] = user_id

    # Добавление новых строк с помощью метода concat()
    df_recommendations = pd.concat([df_recommendations, df_preds.head(limit)], ignore_index=True)

    df_recommendations = df_recommendations[['user_id', 'post_id']]

    posts_id_recommendations = df_recommendations['post_id'].values.tolist()

    posts_recommendations = posts_content[posts_content['post_id'].isin(posts_id_recommendations)]

    posts_recommendations.rename(columns={'post_id': 'id'}, inplace=True)

    posts_recommendations_response = posts_recommendations.to_dict('records')

    return posts_recommendations_response


users_features = load_features()
posts_features = load_posts_features()
posts_content = load_posts_content()
model = load_models()

uvicorn.run(app)