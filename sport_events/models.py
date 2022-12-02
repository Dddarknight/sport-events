from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    sport = Column(String)
    time = Column(String)
    competitor1 = Column(String)
    competitor2 = Column(String)
    date = Column(Date)
    category = Column(String)
