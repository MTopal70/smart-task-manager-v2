"""
Task Database Model.
Represents a single unit of work in the system.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import Base


class Task(Base):
    """
    Represents a task with title, description, and status.
    """
    # pylint: disable=too-few-public-methods

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)

    status = Column(String, default="todo")

    # V2 Features
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="Medium")  # z.B. High, Medium, Low
    category = Column(String, default="General")
    # UTC Zeit verwenden
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Fremdschlüssel
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Beziehungen
    owner = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"
