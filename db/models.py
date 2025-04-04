from sqlalchemy import Column, Integer, String, Text, Boolean, Uuid, TIMESTAMP, CHAR
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
