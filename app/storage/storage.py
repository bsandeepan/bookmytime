from datetime import datetime, timezone
from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.orm import Session
from app.config import settings 
from app.storage.models import UserSettings, Events, Status


class DataStore():
    def __init__(self) -> None:
        self.engine = create_engine(settings.DATABASE_URI.unicode_string())
    
    def sample(self):
        stmt = select(Events)

        results = []
        with Session(self.engine) as session:
            for row in session.execute(stmt).all():
                results.append(row[0].__repr__())
    
        return results

    def fetch_user_settings_by_id(self, user_id: str) -> UserSettings | None:
        stmt = select(UserSettings).where(UserSettings.UserId == user_id)

        with Session(self.engine) as session:
            row = session.execute(stmt).first()

            return row[0] if row else None
    
    def update_user_settings(self, new_settings: UserSettings) -> None:
        with Session(self.engine) as session:
            settings = session.execute(select(UserSettings).where(UserSettings.UserId == new_settings.UserId)).scalar_one()

            settings.Duration = new_settings.Duration
            settings.AvailabilityRules = new_settings.AvailabilityRules
            settings.Timezone = new_settings.Timezone
            settings.UpdatedAt = datetime.now(tz=timezone.utc)

            session.commit()

    def fetch_events_for_user(self, user_id) -> list[Events]:
        stmt = select(Events).filter(
                and_(
                    or_(user_id == Events.OrganizerId, user_id == Events.AttendeeId), 
                    Events.Status == Status.CREATED
            ))

        with Session(self.engine) as session:
            rows = session.execute(stmt).all()

            return [row[0] for row in rows]
        