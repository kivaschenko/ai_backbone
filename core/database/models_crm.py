"""
CRM Data Models
Unified schema for CRM data from multiple sources.
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, Text
from sqlalchemy.sql import func
from .connection import Base


class CRMDeal(Base):
    """Unified deal/opportunity data from CRM systems."""

    __tablename__ = "crm_deals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(
        String(100), nullable=False, index=True
    )  # Original ID from source
    source = Column(String(50), nullable=False, index=True)  # zoho_crm, hubspot, etc.

    # Core deal fields
    name = Column(String(255))
    stage = Column(String(100), index=True)
    amount = Column(Float)
    probability = Column(Float)
    expected_close_date = Column(DateTime)

    # Account/Customer info
    account_name = Column(String(255))
    account_id = Column(String(100))

    # Owner info
    owner_name = Column(String(255))
    owner_id = Column(String(100))

    # Timestamps
    created_time = Column(DateTime, index=True)
    modified_time = Column(DateTime)
    closed_time = Column(DateTime)

    # System timestamps
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data storage
    raw_data = Column(JSON)

    def __repr__(self):
        return (
            f"<CRMDeal(source={self.source}, name={self.name}, amount={self.amount})>"
        )


class CRMContact(Base):
    """Unified contact data from CRM systems."""

    __tablename__ = "crm_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)

    # Contact details
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))

    # Company/Account
    account_name = Column(String(255))
    account_id = Column(String(100))
    title = Column(String(255))

    # Timestamps
    created_time = Column(DateTime, index=True)
    modified_time = Column(DateTime)
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<CRMContact(source={self.source}, name={self.full_name}, email={self.email})>"


class CRMActivity(Base):
    """Activities and interactions from CRM systems."""

    __tablename__ = "crm_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)

    # Activity details
    activity_type = Column(String(100), index=True)  # call, email, meeting, task
    subject = Column(String(500))
    description = Column(Text)
    status = Column(String(50))

    # Related entities
    deal_id = Column(String(100), index=True)
    contact_id = Column(String(100), index=True)
    account_id = Column(String(100), index=True)

    # Owner
    owner_name = Column(String(255))
    owner_id = Column(String(100))

    # Timestamps
    activity_date = Column(DateTime, index=True)
    created_time = Column(DateTime)
    modified_time = Column(DateTime)
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<CRMActivity(type={self.activity_type}, subject={self.subject})>"
