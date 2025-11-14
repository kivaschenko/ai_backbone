"""
Financial Data Models
Unified schema for financial data from accounting systems.
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, Text, Boolean
from sqlalchemy.sql import func
from .connection import Base


class FinanceInvoice(Base):
    """Unified invoice data from accounting systems."""

    __tablename__ = "finance_invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)  # quickbooks, xero, etc.

    # Invoice details
    doc_number = Column(String(100), index=True)
    total_amount = Column(Float, nullable=False)
    balance = Column(Float)  # Outstanding balance
    status = Column(String(50), index=True)  # paid, unpaid, partial, etc.

    # Customer info
    customer_id = Column(String(100), index=True)
    customer_name = Column(String(255))

    # Dates
    invoice_date = Column(DateTime, index=True)
    due_date = Column(DateTime, index=True)
    paid_date = Column(DateTime)

    # Timestamps
    created_time = Column(DateTime)
    modified_time = Column(DateTime)
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<FinanceInvoice(doc_number={self.doc_number}, amount={self.total_amount}, status={self.status})>"


class FinancePayment(Base):
    """Payment transactions from accounting systems."""

    __tablename__ = "finance_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)

    # Payment details
    amount = Column(Float, nullable=False)
    payment_method = Column(String(100))
    reference_number = Column(String(100))

    # Customer info
    customer_id = Column(String(100), index=True)
    customer_name = Column(String(255))

    # Related invoice
    invoice_id = Column(String(100), index=True)

    # Date
    payment_date = Column(DateTime, index=True)

    # Timestamps
    created_time = Column(DateTime)
    modified_time = Column(DateTime)
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<FinancePayment(amount={self.amount}, date={self.payment_date})>"


class FinanceCustomer(Base):
    """Customer/client data from accounting systems."""

    __tablename__ = "finance_customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)

    # Customer details
    display_name = Column(String(255), index=True)
    company_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))

    # Financial info
    balance = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)

    # Status
    active = Column(Boolean, default=True)

    # Timestamps
    created_time = Column(DateTime)
    modified_time = Column(DateTime)
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<FinanceCustomer(name={self.display_name}, balance={self.balance})>"
