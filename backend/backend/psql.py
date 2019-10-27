from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.settings import PSQL_DATABASE

engine = create_engine('postgresql://%s:%s@%s/%s' %
                       (PSQL_DATABASE['USER'], PSQL_DATABASE['PASSWORD'], PSQL_DATABASE['HOST'], PSQL_DATABASE['NAME']))

DBSession = sessionmaker(bind=engine)
Base = declarative_base()
