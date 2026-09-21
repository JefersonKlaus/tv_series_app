from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SeriesModel(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    comment = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="not_started")
    episodes = relationship(
        "EpisodeModel", back_populates="series", cascade="all, delete-orphan"
    )


class EpisodeModel(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False, index=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False)
    name = Column(String(255), nullable=False)
    season = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    watched = Column(Boolean, nullable=False, default=False)
    series = relationship("SeriesModel", back_populates="episodes")
