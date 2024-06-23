from typing import List, DefaultDict
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.dtos import Event, Schedule, DayWiseInfo,AvailabilityRule
from app.storage.storage import DataStore, UserSettings

class SchedulingSvc():
    def __init__(self) -> None:
        self.db = DataStore()
    
    def calculate_time_difference(self, start: datetime, end: datetime) -> timedelta:
        if end < start: # e.g., 23:55-00:25
            end += timedelta(1) # +day
            assert end > start
        
        return end - start
    
    def prepare_events_dict(self, user_id: str, user_tz: str) -> DefaultDict[str, List[Event]]:
        event_orms = self.db.fetch_events_for_user(user_id)
        tz_info = ZoneInfo(user_tz)
        events = defaultdict(list)

        for event in event_orms:
            event.StartTime = event.StartTime.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz_info)
            today = event.StartTime.date().isoformat()
            events[today].append(Event.model_validate(event))

        return events
    
    def prepare_slots(
            self, 
            duration: int, 
            user_tz: str, 
            target_tz: str, 
            availability: AvailabilityRule | None, 
            booked_slots: List[str], 
            today: datetime
        ) -> List[str]:
        slots = []
        to_tz = ZoneInfo(target_tz)
        from_tz = ZoneInfo(user_tz)

        if (availability and len(availability.Hours) > 0):
            for period in availability.Hours:
                # I take each avaialbility list [start, end] and calculate total difference(mins) / duration => no of slots
                start, end = [
                    datetime.strptime(t, '%H:%M').replace(tzinfo=from_tz, day=today.day, month=today.month, year=today.year).replace(tzinfo=to_tz) 
                    for t in period]
                time_diff = self.calculate_time_difference(start, end).seconds // 60
                possible_slots = time_diff // duration
                # I start creating new slots by adding duration to start time, and get end time for slot 1 -> push in list
                for _ in range(possible_slots):
                    is_slot_clear = True
                    for b in booked_slots:
                        diff = start - b if start > b else b - start

                        if diff.seconds // 60 < duration:
                            is_slot_clear = False
                            break
                    
                    if is_slot_clear:
                        slots.append(start.strftime("%H:%M"))
                    # I repeat for slot 2, 3, ...N
                    start += timedelta(minutes=duration)

        return slots
    
    def prepare_day_wise_info_list(self, events:  DefaultDict[str, List[Event]], settings: UserSettings, to_tz: str):
        day_wise_info_list = []
        for i in range(settings.MaxCalenderDays):
            today = datetime.now() + timedelta(days=i)
            today_date = today.date().isoformat()
            weekday = today.strftime("%A").lower()
            availability = settings.get_availability_rule(weekday)
            booked_slots = [b.StartTime for b in events[today_date]]
            slots = self.prepare_slots(settings.Duration, settings.Timezone, to_tz, availability, booked_slots, today)
            
            day_wise_info_list.append(DayWiseInfo(
                Date=today.date(),
                Slots=slots,
                Events=events[today_date]
            ))
                
        return day_wise_info_list

    def prepare_user_schedule(self, user_id: str, to_tz: str = "") -> Schedule:
        user_settings = self.db.fetch_user_settings_by_id(user_id)

        to_tz = to_tz if to_tz else user_settings.Timezone

        events = self.prepare_events_dict(user_id, to_tz)

        schedule = Schedule(
            UserId=user_id,
            Duration=user_settings.Duration,
            Timezone=to_tz,
            Schedule=self.prepare_day_wise_info_list(events, user_settings, to_tz)
        )

        return schedule
    
    def prepare_user_schedule_overlapping(self, user_id: str, attendee_id: str):
        user_settings = self.db.fetch_user_settings_by_id(user_id)
        attendee_settings = self.db.fetch_user_settings_by_id(attendee_id)
        to_tz = attendee_settings.Timezone
        to_tz_info = ZoneInfo(to_tz)

        events = self.prepare_events_dict(user_id, to_tz)

        user_schedule = Schedule(
            UserId=user_id,
            Duration=user_settings.Duration,
            Timezone=to_tz,
            Schedule=self.prepare_day_wise_info_list(events, user_settings, to_tz)
        )

        for daily_info in user_schedule.Schedule:
            weekday = daily_info.Date.strftime("%A").lower()
            related_rule = attendee_settings.get_availability_rule(weekday)
            slots = []
            if not related_rule:
                daily_info.Slots = slots,
                daily_info.Events = [],
            else:
            # does slot overlap with rule timeframe?
            # for each timeframe, start <= slot < end
                for timeframe in related_rule.Hours:
                    start, end = [datetime.strptime(t, '%H:%M').replace(tzinfo=to_tz_info) for t in timeframe]
                    slots.extend(filter(lambda x: start <= datetime.strptime(x, '%H:%M').replace(tzinfo=to_tz_info) < end, daily_info.Slots))
            
                daily_info.Slots = slots
        
        return user_schedule

                


        
