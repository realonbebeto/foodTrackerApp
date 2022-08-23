from datetime import datetime, timezone

from sqlalchemy import (Column, Date, DateTime, ForeignKey, Integer, String,
                        Table)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy_utils import EmailType

from .database import Base

assoc_table = Table(
    "log_food",
    Base.metadata,
    Column("log_id", ForeignKey("logs.id"), primary_key=True),
    Column("food_id", ForeignKey("foods.id"), primary_key=True),
)


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    food_name = Column(String, nullable=False, unique=True)
    proteins = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True),
                        onupdate=datetime.now(timezone.utc))

    @property
    def calories(self):
        return self.proteins * 4 + self.carbs * 4 + self.fats * 9


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, nullable=False)
    when = Column(Date, nullable=False, unique=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True),
                        onupdate=datetime.now(timezone.utc))
    foods = relationship("Food", secondary=assoc_table,
                         backref="logs", lazy="dynamic")
