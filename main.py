from typing import List
from fastapi import FastAPI

from app.storage.storage import DataStore
from app.storage import models
from app.service.schedule import SchedulingSvc
from app import dtos

app = FastAPI()
db = DataStore()
svc = SchedulingSvc()

@app.get("/")
def read_root():
    return {"Hello": db.sample()}

@app.get("/User/{user_id}/Settings")
def get_user_settings(user_id: str):
    # todo: add validation check for userid
    record: models.UserSettings = db.fetch_user_settings_by_id(user_id)

    return dtos.UserSettings.model_validate(record)

@app.get("/User/{user_id}/Schedule")
def get_user_schedule(user_id: str) -> dtos.Schedule:
    schedule = svc.prepare_user_schedule(user_id)

    return schedule
