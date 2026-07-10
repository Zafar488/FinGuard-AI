from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Customer(Base):
    __tablename__ = "customers"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Indexed for fast lookups
    customer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    account_status = Column(String, default="NEW") # e.g., VIP, NEW, SUSPENDED
    country_of_origin = Column(String, nullable=False)
    avg_monthly_spend = Column(Float, default=0.0)
    
    # Industry Standard Timestamps (managed by the DB, not Python)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to transactions table
    transactions = relationship("TransactionRecord", back_populates="customer", cascade="all, delete-orphan")

class TransactionRecord(Base):
    __tablename__ = "transactions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Indexed for fast lookups
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    
    # Proper Foreign Key linking back to the Customer table
    customer_id = Column(String, ForeignKey("customers.customer_id"), index=True, nullable=False)
    
    # Transaction Details
    amount = Column(Float, nullable=False)
    ml_risk_score = Column(Float, nullable=False)
    is_blocked = Column(Boolean, default=False)
    agent_action = Column(String, nullable=True) # e.g., ESCALATE, AUTO-DISMISS
    
    # Industry Standard Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship back to customer
    customer = relationship("Customer", back_populates="transactions")