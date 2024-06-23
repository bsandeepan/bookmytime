from pydantic import BaseModel, ConfigDict, Field, UUID4, field_validator
from datetime import datetime, date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from app.common import UserIdRx, MinDuration, MaxDuration, Weekdays

class AvailabilityRule(BaseModel):
    Day: str
    Hours: list[tuple[str, str]]

    @field_validator("Day")
    @classmethod
    def is_day_a_valid_weekday(cls, v: str) -> str:
        if v.lower() not in Weekdays:
            raise ValueError(f"{v} is not a weekday.")
        
        return v.lower()
    
    @field_validator("Hours")
    @classmethod
    def is_day_a_valid_weekday(cls, hours: list[list[str]]) -> list[list[str]]:
        for period in hours:
            try:
                datetime.strptime(period[0], "%H:%M")
                datetime.strptime(period[1], "%H:%M")
            except ValueError as e:
                raise ValueError(f"Timestrings need to be in HH:MM format: {period}")
        
        return hours

class UserSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    UserId: str = Field(..., pattern=UserIdRx)
    Duration: int
    Timezone: str
    AvailabilityRules: list[AvailabilityRule] | None

    @field_validator("Duration")
    @classmethod
    def is_duration_value_acceptable(cls, v: int) -> int:
        if not (MinDuration <= v <=MaxDuration and v % MinDuration == 0):
            raise ValueError(f"Duration must be a multiple of {MinDuration} and cannot be greater than {MaxDuration} minutes.")
        return v
    
    @field_validator("Timezone")
    @classmethod
    def is_timezone_iana_compliant(cls, v: str) -> str:
        try:
            _ = ZoneInfo(v)
        except ZoneInfoNotFoundError as e:
            raise ValueError("Timezone value is not compliant with IANA timezones.")
        else:
            return v

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
    Slots: list[str] | None
    Events: list[Event] | None

class Schedule(BaseModel):
    UserId: str
    Duration: int
    Timezone: str
    Schedule: list[DayWiseInfo]
