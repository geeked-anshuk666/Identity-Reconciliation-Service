from pydantic import BaseModel, Field
from typing import List

class ContactResponse(BaseModel):
    """Response schema containing consolidated contact information"""
    primaryContatctId: int = Field(
        ..., 
        alias="primaryContatctId",
        description="ID of the primary contact record"
    )
    emails: List[str] = Field(
        ..., 
        description="All email addresses associated with this contact"
    )
    phoneNumbers: List[str] = Field(
        ..., 
        description="All phone numbers associated with this contact"
    )
    secondaryContactIds: List[int] = Field(
        ..., 
        description="IDs of secondary contact records linked to this primary"
    )

class IdentifyResponse(BaseModel):
    """Top-level response schema for the identity reconciliation endpoint"""
    contact: ContactResponse = Field(
        ..., 
        description="Consolidated contact information"
    )