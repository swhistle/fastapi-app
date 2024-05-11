import os
from dotenv import load_dotenv


load_dotenv()

def build_db_url(db, host, user, password, port):
    return f'postgresql://{user}:{password}@{host}:{port}/{db}'


connection_url = build_db_url(
    db=os.environ["POSTGRES_DATABASE"],
    host=os.environ["POSTGRES_HOST"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    port=int(os.environ["POSTGRES_PORT"])
)