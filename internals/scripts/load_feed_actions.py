import pandas as pd

from internals.db_connection.connection import connection_url

df = pd.read_sql(
    """ SELECT * FROM feed_action """,
    connection_url
)

# Attention! This is a very large table, over 60 million rows and 2 gb.
# Better use a script 'load_feed_actions_last_10.py' to load the last 10 feed_actions items for each user
df.to_csv('internals/data/feed_actions.csv', index=False, sep=';')