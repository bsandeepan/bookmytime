from typing import List, Tuple
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

    def fetch_user_settings_by_id(self, user_id: str) -> UserSettings:
        stmt = select(UserSettings).where(UserSettings.UserId == user_id)

        with Session(self.engine) as session:
            row = session.execute(stmt).first()

            # todo: Handle not found error
            return row[0]

    def fetch_events_for_user(self, user_id) -> List[Events]:
        stmt = select(Events).filter(
                and_(
                    or_(user_id == Events.OrganizerId, user_id == Events.AttendeeId), 
                    Events.Status == Status.CREATED
            ))
        
        print(stmt)

        with Session(self.engine) as session:
            rows = session.execute(stmt).all()
            print(rows)

            return [row[0] for row in rows]
        