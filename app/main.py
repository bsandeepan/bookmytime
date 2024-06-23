from fastapi import FastAPI, Path, HTTPException
from typing import Annotated

from app.storage.storage import DataStore
from app.storage import models
from app.service.schedule import SchedulingSvc
from app import dtos
from app.common import UserIdRx

app = FastAPI()
db = DataStore()
svc = SchedulingSvc()

userIdPathType = Annotated[str, Path(title="User Id", pattern=UserIdRx)]

@app.get("/")
def read_root():
    return {"Hello": db.sample()}

@app.get("/User/{user_id}/Settings")
def get_user_settings(user_id: userIdPathType):
    res = svc.fetch_user_settings(user_id)

    if res is None:
        raise HTTPException(status_code=404)
    
    return res

@app.put("/User/{user_id}/Settings", status_code=204)
def update_user_settings(user_id: userIdPathType, settings: dtos.UserSettings) -> None:
    if user_id != settings.UserId:
        # if user is updating anothers settings, take action.
        raise HTTPException(status_code=401, detail="User id mismatch")
    
    svc.update_user_settings(settings)
    return None

@app.get("/User/{user_id}/Schedule")
def get_user_schedule(user_id: userIdPathType, to_tz: str = "") -> dtos.Schedule:
    schedule = svc.prepare_user_schedule(user_id, to_tz)

    return schedule

@app.get("/User/{user_id}/Schedule/Overlap/{attendee_id}")
def get_overlap_with_user_schedule(user_id: userIdPathType, attendee_id: userIdPathType) -> dtos.Schedule:
    overlapping_schedule = svc.prepare_user_schedule_overlapping(user_id, attendee_id)

    return overlapping_schedule

@app.post("/User/{user_id}/Schedule/Event", status_code=201)
def create_new_meeting_event(user_id: userIdPathType, event: dtos.Event) -> None:
    if user_id != event.OrganizerId:
        # user is not adding event to organizer's schedule.
        raise HTTPException(status_code=401, detail="Organizer id mismatch")
    
    try:
        svc.book_event(event)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return None
