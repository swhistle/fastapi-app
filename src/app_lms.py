import os
from catboost import CatBoostClassifier

from fastapi import FastAPI, HTTPException
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
from typing import List

from schema import PostGet

connection_url = "postgresql://robot-startml-ro:pheiph0hahj1Vaif@postgres.lab.karpov.courses:6432/startml"

#Загрузка модели
def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально.
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH

def load_models():
    model_path = get_model_path("catBoost_classifier")
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

users_features = load_features()
posts_features = load_posts_features()
posts_content = load_posts_content()
model = load_models()

app = FastAPI()

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