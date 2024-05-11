import pandas as pd

from internals.db_connection.connection import connection_url

df = pd.read_sql(
    """SELECT * FROM post""",
    connection_url
)

df.to_csv('internals/data/posts.csv', index=False, sep=';')