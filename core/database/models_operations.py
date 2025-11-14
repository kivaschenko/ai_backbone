"""
Operations Data Models
Time tracking and operational data.
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, Date
from sqlalchemy.sql import func
from .connection import Base


class OperationsTimeLog(Base):
    """Time tracking data from time management systems."""

    __tablename__ = "operations_time_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)  # time_doctor, toggl, etc.

    # User details
    user_id = Column(String(100), index=True)
    user_name = Column(String(255))
    user_email = Column(String(255))

    # Work details
    project_name = Column(String(255), index=True)
    task_name = Column(String(500))
    description = Column(String(1000))

    # Time
    duration_seconds = Column(Integer, nullable=False)
    duration_hours = Column(Float)  # Calculated from seconds
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    date = Column(Date, index=True)

    # Billable
    is_billable = Column(Integer, default=1)  # 1 = billable, 0 = non-billable
    hourly_rate = Column(Float)
    total_cost = Column(Float)

    # Timestamps
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<OperationsTimeLog(user={self.user_name}, project={self.project_name}, hours={self.duration_hours})>"

    def calculate_duration_hours(self):
        """Convert seconds to hours."""
        if self.duration_seconds:
            self.duration_hours = self.duration_seconds / 3600

    def calculate_cost(self):
        """Calculate total cost based on hourly rate."""
        if self.duration_hours and self.hourly_rate:
            self.total_cost = self.duration_hours * self.hourly_rate


class OperationsProject(Base):
    """Project data for tracking work and budgets."""

    __tablename__ = "operations_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)

    # Project details
    project_name = Column(String(255), nullable=False, index=True)
    client_name = Column(String(255))
    status = Column(String(50), index=True)  # active, completed, on_hold

    # Financial
    budget = Column(Float)
    total_hours = Column(Float)
    total_cost = Column(Float)

    # Dates
    start_date = Column(Date)
    end_date = Column(Date)

    # Timestamps
    created_time = Column(DateTime)
    modified_time = Column(DateTime)
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<OperationsProject(name={self.project_name}, status={self.status})>"
