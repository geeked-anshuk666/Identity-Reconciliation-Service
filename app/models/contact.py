from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Contact(Base):
    """Contact model for storing customer identity information
    
    Supports linking multiple contact records for the same customer through
    primary-secondary relationships. Each customer has one primary contact
    record and zero or more secondary records linked to it.
    """
    __tablename__ = "contacts"
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        description="Unique identifier for this contact record"
    )
    phone_number = Column(
        String, 
        nullable=True, 
        index=True,
        description="Customer's phone number"
    )
    email = Column(
        String, 
        nullable=True, 
        index=True,
        description="Customer's email address"
    )
    linked_id = Column(
        Integer, 
        ForeignKey("contacts.id"), 
        nullable=True, 
        index=True,
        description="ID of primary contact this record is linked to (for secondary records only)"
    )
    link_precedence = Column(
        String, 
        nullable=False,
        description="Whether this is a 'primary' or 'secondary' contact record"
    )
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        description="Timestamp when this record was created"
    )
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False,
        description="Timestamp when this record was last updated"
    )
    deleted_at = Column(
        DateTime, 
        nullable=True,
        description="Timestamp when this record was soft-deleted (null if active)"
    )
    
    # Self-referential relationship for linked contacts
    linked_contact = relationship("Contact", remote_side=[id], backref="secondary_contacts")
    
    # Database indexes for improved query performance
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_phone_number', 'phone_number'),
        Index('idx_linked_id', 'linked_id'),
    )