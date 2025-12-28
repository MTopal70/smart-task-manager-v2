"""
Project Database Model.
Groups multiple tasks together.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Project(Base):
    """
    Represents a project that contains multiple tasks.
    """
    # pylint: disable=too-few-public-methods

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Beziehungen
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
