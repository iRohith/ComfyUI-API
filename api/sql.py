import os
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

Base = automap_base()
engine = create_engine(
    os.environ["DB_URL"],
    echo=False,
)
Base.prepare(engine, reflect=True)

Users = Base.classes.users
Models = Base.classes.models
Favorites = Base.classes.favorites
Prompts = Base.classes.prompts

# Create a sessionmaker bound to the engine
Session = sessionmaker(bind=engine)

# Create a session
session = Session()
