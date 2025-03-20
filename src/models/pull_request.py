
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import enum



class Status(enum.Enum):
    CREATED = "created"
    APPROVED = "approved"
    MERGED = "merged"
    CLOSED = "closed"
    FAILED = "failed"


class PullRequest(Base):
    __tablename__ = 'pull_requests'

    id = Column(Integer, primary_key=True)
    oci_id = Column(String, unique=True, nullable=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source_branch = Column(String, nullable=False)
    target_branch = Column(String, nullable=False)
    status = Column(Enum(Status), default=Status.CREATED)
    markdown_file = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    repository = relationship("Repository", back_populates="pull_requests")
    tasks = relationship("Task", back_populates="pull_request")

    def __repr__(self):
        return f"<PullRequest(title='{self.title}', status='{self.status}')>"


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    celery_task_id = Column(String, unique=True, nullable=False)
    task_type = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    result = Column(Text, nullable=True)
    pull_request_id = Column(Integer, ForeignKey('pull_requests.id'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    pull_request = relationship("PullRequest", back_populates="tasks")

    def __repr__(self):
        return f"<Task(celery_task_id='{self.celery_task_id}', status='{self.status}')>"