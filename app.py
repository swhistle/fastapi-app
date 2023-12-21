import datetime
from fastapi import Depends, FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from schema import UserGet, PostGet

def get_db():
    connection = psycopg2.connect(
        database='startml',
        host='postgres.lab.karpov.courses',
        user='robot-startml-ro',
        password='pheiph0hahj1Vaif',
        port=6432,
        cursor_factory=RealDictCursor
    )

    return connection

app = FastAPI()

@app.get("/")
def root() -> str:
    return 'root'

@app.get('/sum_date')
def sum_date(current_date: datetime.date, offset: int):
    return current_date + datetime.timedelta(days=offset)

@app.post('/user/validate')
def validate(user: UserGet):
    return f'Will add user: {user.name} {user.surname} with age {user.age}'

@app.get('/user/{id}', response_model=UserGet)
def user(id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""SELECT * FROM "user" WHERE id='%s'""" % id)
        results = cursor.fetchone()

        if not results:
            raise HTTPException(404, detail='user not found')

        return UserGet(**results)

@app.get('/post/{id}', response_model=PostGet)
def user(id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""SELECT id, text, topic FROM "post" WHERE id='%s'""" % id)
        results = cursor.fetchone()

        if not results:
            raise HTTPException(404, detail='post not found')

        return PostGet(**results)
