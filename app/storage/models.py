import enum
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import SMALLINT, String, DATETIME, JSON, UUID, TEXT, Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

class Base(DeclarativeBase):
    pass

class AvailabilityRule(BaseModel):
    Day: str
    Hours: list[tuple[str, str] | None]

class UserSettings(Base):
    __tablename__ = "UserSettings"

    UserId: Mapped[str] = mapped_column(String(10), primary_key=True)
    Duration: Mapped[int] = mapped_column(SMALLINT)
    Timezone: Mapped[str] = mapped_column(String(40))
    MaxCalenderDays: Mapped[int] = mapped_column(SMALLINT)
    UpdatedAt: Mapped[datetime] = mapped_column(DATETIME)
    AvailabilityRules: Mapped[list[AvailabilityRule]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<{self.__tablename__} (id={self.UserId}, Timezone={self.Timezone})>"
    
    def get_availability_rule(self, weekday: str, default=None) -> AvailabilityRule | None:
        for rule in self.AvailabilityRules:
            rule = AvailabilityRule.model_validate_json(rule)
            if rule.Day == weekday.lower():
                return rule
        
        return default

class Status(enum.Enum):
    CREATED = "CREATED"
    HAPPENED = "HAPPENED"
    CANCELLED = "CANCELLED"
    DECLINED = "DECLINED"

class Events(Base):
    __tablename__ = "Events"

    EventId: Mapped[str] = mapped_column(UUID, primary_key=True)
    OrganizerId: Mapped[str] = mapped_column(String(10), ForeignKey("UserSettings.UserId"))
    AttendeeId: Mapped[str] = mapped_column(String(10), ForeignKey("UserSettings.UserId"))
    StartTime:Mapped[datetime] = mapped_column(DATETIME)
    Duration: Mapped[int] = mapped_column(SMALLINT)
    CreatedAt: Mapped[datetime] = mapped_column(DATETIME)
    UpdatedAt: Mapped[datetime] = mapped_column(DATETIME)
    Notes: Mapped[str | None] = mapped_column(TEXT)
    Status: Mapped[str] = mapped_column(Enum(Status, length=10, native_enum=False))

    organizer = relationship(
        "UserSettings",
        primaryjoin="Events.OrganizerId == UserSettings.UserId",
        foreign_keys=OrganizerId,
    )

    attendee = relationship(
        "UserSettings",
        primaryjoin="Events.AttendeeId == UserSettings.UserId",
        foreign_keys=AttendeeId,
    )

    def __repr__(self) -> str:
        return f"<{self.__tablename__} (id={self.EventId}, Organizer={self.OrganizerId}, Attendee={self.AttendeeId})>"