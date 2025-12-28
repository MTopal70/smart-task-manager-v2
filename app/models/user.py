"""
User Database Model.
Defines the User table and its relationships.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    """
    Represents a registered user in the system.
    """
    # pylint: disable=too-few-public-methods

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    # Verwende UTC Zeit für globale Konsistenz
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Beziehungen
    tasks = relationship("Task", back_populates="owner")
    projects = relationship("Project", back_populates="owner")

    def __repr__(self):
        """String representation for debugging."""
        return f"<User(id={self.id}, username='{self.username}')>"
