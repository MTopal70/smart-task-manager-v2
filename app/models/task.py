# task model

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String)

    # V2 Features
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="Medium")  # z.B. High, Medium, Low
    category = Column(String, default="General")
    created_at = Column(DateTime, default=lambda:  datetime.now(timezone.utc))

    # Fremdschlüssel
    # 1. Ein Task MUSS einen Owner haben (nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 2. Ein Task KANN ein Projekt haben (nullable=True ist Standard, aber hier implizit)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Beziehungen
    owner = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
