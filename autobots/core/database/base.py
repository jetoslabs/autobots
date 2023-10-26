from typing import Generator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker, Session

from autobots.core.settings import SettingsProvider

settings = SettingsProvider.sget()
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
SessionLocal: sessionmaker = sessionmaker(bind=engine, autocommit=False, autoflush=False)

metadata = MetaData(schema=settings.SQLALCHEMY_DATABASE_SCHEMA)
# Creating Base for so Alembic sees only models in this App
Base = declarative_base(metadata=metadata)


def create_database_schema():
    Base.metadata.create_all(engine)


create_database_schema()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
