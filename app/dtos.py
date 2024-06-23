from pydantic import BaseModel, ConfigDict, Field, UUID4
from datetime import datetime, date
from typing import List

class AvailabilityRule(BaseModel):
    Day: str
    Hours: List[List[str]]

class UserSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    UserId: str
    Duration: int
    Timezone: str
    AvailabilityRules: List[AvailabilityRule] | None

class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    EventId: UUID4
    OrganizerId: str
    AttendeeId: str
    StartTime: datetime
    Duration: int
    Notes: str
    Status: str = Field(..., exclude=True)
    UpdatedAt: datetime = Field(..., exclude=True)

class DayWiseInfo(BaseModel):
    Date: date
    Slots: List[str] | None
    Events: List[Event] | None

class Schedule(BaseModel):
    UserId: str
    Duration: int
    Timezone: str
    Schedule: List[DayWiseInfo]
