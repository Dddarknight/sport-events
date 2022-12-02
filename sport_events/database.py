import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from sport_events.models import Event, Base


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)


def migrate(sports):
    with Session(engine) as session:
        db_events = []
        for sport in sports.keys():
            if sport:
                if sports[sport].get('events') is None:
                    continue
                for event in sports[sport]['events']:
                    db_event = Event(
                        sport=sport,
                        time=event['time'],
                        competitor1=event['competitors'][0],
                        competitor2=event['competitors'][1],
                        date=datetime.now().date(),
                        category=event['category'],
                    )
                    db_events.append(db_event)

        session.add_all(db_events)
        session.commit()
