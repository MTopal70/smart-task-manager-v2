from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Wichtig für den Kalender: Wann geht's los?
    start_date = Column(DateTime, default=datetime.now)

    # Wer ist der Chef?
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Beziehungen
    owner = relationship("app.models.user.User", back_populates="projects")
    tasks = relationship("app.models.task.Task", back_populates="project", cascade="all, delete")