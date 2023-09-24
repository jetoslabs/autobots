from typing import Generator
#
from sqlalchemy.orm import Session
#
from autobots.database import base
#

def get_db() -> Generator[Session, None, None]:
     return base.get_db()
