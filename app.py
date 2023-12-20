import datetime
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root() -> str:
    return 'root'

@app.get('/sum_date')
def sum_date(current_date: datetime.date, offset: int):
    return current_date + datetime.timedelta(days=offset)
