from sqlalchemy import Column, Integer, String, Text, Uuid, TIMESTAMP, CHAR, DATE
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Institute(Base):
    __tablename__ = "institutions"

    institution_id = Column(
        Uuid, primary_key=True, server_default=str("gen_random_uuid()")
    )
    name = Column(Text, unique=True, nullable=False)
    website = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    state_id = Column(Uuid, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now())
    updated_at = Column(TIMESTAMP, default=datetime.now())

    def __repr__(self):
        return f"<name='{self.name}')>"


class State(Base):
    __tablename__ = "states"

    state_id = Column(Uuid, primary_key=True, server_default=str("gen_random_uuid()"))
    name = Column(Text, unique=True, nullable=False)
    abbreviation = Column(CHAR(2), unique=True, nullable=False)

    def __repr__(self):
        return f"<name='{self.name}')>"


class Program(Base):
    __tablename__ = "programs"

    program_id = Column(Uuid, primary_key=True, server_default=str("gen_random_uuid()"))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    degree_level = Column(String(50), nullable=True)
    duration_months = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now())
    updated_at = Column(TIMESTAMP, default=datetime.now())

    def __repr__(self):
        return f"<name='{self.name}')>"


class Announcement(Base):
    __tablename__ = "announcements"

    announcement_id = Column(
        Uuid, primary_key=True, server_default=str("gen_random_uuid()")
    )
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(255), nullable=False)
    institution_id = Column(Uuid, nullable=False)
    state_id = Column(Uuid, nullable=False)
    published_date = Column(DATE, nullable=True)
    application_open_date = Column(DATE, nullable=True)
    application_deadline = Column(DATE, nullable=True)
    term = Column(String(50), nullable=True)
    contact_info = Column(Text, nullable=True)
    announcement_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now())
    updated_at = Column(TIMESTAMP, default=datetime.now())
    search_vector = Column(
        String(255), nullable=True, index=True, server_default="''::character varying"
    )

    def __repr__(self):
        return f"<title='{self.title}')>"


class AnnouncementProgram(Base):
    __tablename__ = "program_announcements"
    announcement_id = Column(Uuid, primary_key=True)
    program_id = Column(Uuid, primary_key=True)

    def __repr__(self):
        return f"<announcement_id='{self.announcement_id}', program_id='{self.program_id}')>"
