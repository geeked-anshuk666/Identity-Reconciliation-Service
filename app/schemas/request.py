from pydantic import BaseModel, Field, model_validator
from typing import Optional

class IdentifyRequest(BaseModel):
    email: Optional[str] = None
    phoneNumber: Optional[str] = Field(None, alias="phoneNumber")
    
    @model_validator(mode='after')
    def at_least_one_field(self):
        if not self.email and not self.phoneNumber:
            raise ValueError('At least one of email or phoneNumber must be provided')
        return self
    
    class Config:
        populate_by_name = True