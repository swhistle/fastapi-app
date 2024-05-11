import pandas as pd

from internals.db_connection.connection import connection_url

df = pd.read_sql(
    """ SELECT * FROM "user" """,
    connection_url
)

df.to_csv('internals/data/users.csv', index=False, sep=';')