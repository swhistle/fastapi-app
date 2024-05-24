import pandas as pd
from sqlalchemy import create_engine

from internals.db_connection.connection import connection_url

engine = create_engine(connection_url)

df_posts_features = pd.read_csv('internals/data/data_posts_features.csv', sep=';')
df_posts_features.to_sql('al-svistunov_posts_features_lesson_22', con=engine, if_exists="replace")

df_users_features = pd.read_csv('internals/data/data_users_features.csv', sep=';')
df_users_features.to_sql('al-svistunov_users_features_lesson_22', con=engine, if_exists="replace")