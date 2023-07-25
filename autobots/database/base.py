from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

from autobots.core.settings import get_settings

engine = create_engine(get_settings().SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)

metadata = MetaData(schema=get_settings().SQLALCHEMY_DATABASE_SCHEMA)
# Creating Base for so Alembic sees only models in this App
Base = declarative_base(metadata=metadata)


def create_database_schema():
    Base.metadata.create_all(engine)


create_database_schema()


