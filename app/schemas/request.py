from pydantic import BaseModel, Field, model_validator
from typing import Optional

class IdentifyRequest(BaseModel):
    """Request schema for identifying and consolidating customer contacts"""
    email: Optional[str] = Field(
        None, 
        description="Customer's email address"
    )
    phoneNumber: Optional[str] = Field(
        None, 
        alias="phoneNumber",
        description="Customer's phone number"
    )
    
    @model_validator(mode='after')
    def at_least_one_field(self):
        """Ensure at least one contact field is provided"""
        if not self.email and not self.phoneNumber:
            raise ValueError('At least one of email or phoneNumber must be provided')
        return self
    
    class Config:
        populate_by_name = True