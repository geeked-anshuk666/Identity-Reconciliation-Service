from pydantic import BaseModel, Field
from typing import List

class ContactResponse(BaseModel):
    primaryContatctId: int = Field(..., alias="primaryContatctId")  # Note: typo in spec
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]
    
    class Config:
        populate_by_name = True

class IdentifyResponse(BaseModel):
    contact: ContactResponse