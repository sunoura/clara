from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from contextlib import contextmanager
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv

# Import all models to register them with SQLModel
from data.models import (
    MemoryCollection,
    MemoryDocument,
    InteractionSession,
    InteractionPayload,
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./sqlite.db"

if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)


engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
    except OperationalError as e:
        print("OperationalError while creating DB and tables:", e)
        print("Check if the database file path is valid and the directory exists.")


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@contextmanager
def session_from_generator():
    gen = get_session()
    db = next(gen)
    try:
        yield db
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


def reset_database():
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)