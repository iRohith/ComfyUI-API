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

# Create a sessionmaker bound to the engine
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = "users"

    username = Column(Text, primary_key=True)
    subscription = Column(Text, nullable=False, server_default=text("'0'::text"))
    tokens = Column(Integer, nullable=False, server_default=text("100"))
    last_active = Column(DateTime, nullable=False, server_default=text("now()"))


class Model(Base):
    __tablename__ = "models"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('models_id_seq'::regclass)"),
    )
    display_name = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=False, server_default=text("''::text"))
    url = Column(Text, nullable=False, unique=True)
    image_url = Column(
        Text,
        nullable=False,
        server_default=text(
            "'https://imagedelivery.net/9UaeqBrXzrQ9mC5U6QFATQ/9fd6401f-cb5c-4d3f-4f9f-15fb7d76e600/public'::text"
        ),
    )
    base_model_type = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    ext = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    created_by = Column(ForeignKey("users.username"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    favorite_count = Column(Integer, nullable=False, server_default=text("0"))

    user = relationship("User")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('favorites_id_seq'::regclass)"),
    )
    username = Column(ForeignKey("users.username"), nullable=False)
    model_id = Column(ForeignKey("models.id"), nullable=False)

    model = relationship("Model")
    user = relationship("User")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('prompts_id_seq'::regclass)"),
    )
    created_by = Column(ForeignKey("users.username"), nullable=False)
    type = Column(Text, nullable=False)
    params = Column(Text, nullable=False)
    model = Column(ForeignKey("models.display_name"))
    created_at = Column(DateTime, server_default=text("now()"))

    user = relationship("User")
    model1 = relationship("Model")
