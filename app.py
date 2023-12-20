import datetime
from fastapi import FastAPI
from pydantic import BaseModel


class User(BaseModel):
    gender: int
    age: int
    city: str

    class Config:
        orm_mode = True


app = FastAPI()

@app.get("/")
def root() -> str:
    return 'root'

@app.get('/sum_date')
def sum_date(current_date: datetime.date, offset: int):
    return current_date + datetime.timedelta(days=offset)

@app.post('/user/validate')
def validate(user: User):
    return f'Will add user: {user.name} {user.surname} with age {user.age}'
