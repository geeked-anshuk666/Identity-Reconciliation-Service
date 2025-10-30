from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.request import IdentifyRequest
from app.schemas.response import IdentifyResponse
from app.services.identity_service import IdentityService
from app.database import get_db

router = APIRouter()

@router.post("/identify", response_model=IdentifyResponse, status_code=200)
async def identify(
    request: IdentifyRequest,
    db: AsyncSession = Depends(get_db)
) -> IdentifyResponse:
    """
    Identify and consolidate customer contact information.
    
    - **email**: Customer email (optional if phoneNumber provided)
    - **phoneNumber**: Customer phone number (optional if email provided)
    
    Returns consolidated contact information with primary and secondary contacts.
    """
    service = IdentityService(db)
    result = await service.identify_contact(request.email, request.phoneNumber)
    return result