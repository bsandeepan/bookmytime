from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from app.dtos import Event, Schedule, DayWiseInfo
from app.storage.storage import DataStore

class SchedulingSvc():
    def __init__(self) -> None:
        self.db = DataStore()
    
    def prepare_events_list(self, user_id: str, user_tz: str) -> List[Event]:
        event_orms = self.db.fetch_events_for_user(user_id)
        tz_info = ZoneInfo(user_tz)
        events = []

        for event in event_orms:
            event.StartTime = event.StartTime.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz_info)
            events.append(Event.model_validate(event))

        return events
    
    def prepare_user_schedule(self, user_id: str, to_tz: str = ""):
        user_settings = self.db.fetch_user_settings_by_id(user_id)

        to_tz = to_tz if to_tz else user_settings.Timezone

        events = self.prepare_events_list(user_id, to_tz)
        today = datetime.today().date()

        schedule = Schedule(
            UserId=user_id,
            Duration=user_settings.Duration,
            Timezone=to_tz,
            Schedule=[
                DayWiseInfo(Date=today, Slots=[], Events=events),
            ]
        )

        return schedule


        
