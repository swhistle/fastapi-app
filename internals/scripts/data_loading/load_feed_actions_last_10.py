import pandas as pd

from internals.db_connection.connection import connection_url

df = pd.read_sql(
    """ 
    SELECT
    *
    FROM
    (
    SELECT
      user_id,
      post_id,
      action,
      time,
      ROW_NUMBER() OVER (
        PARTITION BY user_id
        ORDER BY
          time DESC
      ) as row_number
    FROM
      feed_action
    ORDER BY
      user_id,
      time DESC
  ) AS data
  WHERE data.row_number <= 10
    """,
    connection_url
)

df.to_csv('internals/data/feed_actions_last_10.csv', index=False, sep=';')