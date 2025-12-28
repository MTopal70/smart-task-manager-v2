#project model

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    # Fremdschlüssel: Ein Projekt gehört zwingend einem User
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Beziehungen
    owner = relationship("User", back_populates="projects")
    # cascade="all, delete" bedeutet: Wenn Projekt gelöscht wird, werden auch die Tasks gelöscht (optional)
    tasks = relationship("Task", back_populates="project")

