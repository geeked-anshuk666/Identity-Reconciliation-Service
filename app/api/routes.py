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
    
    This endpoint handles the core identity reconciliation logic, taking customer
    contact information (email and/or phone number) and returning a consolidated
    view of all related contacts.
    
    The service intelligently links contacts based on the four scenarios:
    - New customer (creates primary contact)
    - Partial match (adds new info to existing contact)
    - Exact match (returns existing contact)
    - Linking two existing contacts (merges contact histories)
    
    Args:
        request: IdentifyRequest containing email and/or phoneNumber
        db: Database session (injected by FastAPI)
    
    Returns:
        IdentifyResponse with consolidated contact information
    """
    # Initialize the identity service with the database session
    identity_service = IdentityService(db)
    
    # Process the customer contact information
    customer_response = await identity_service.identify_contact(
        request.email, 
        request.phoneNumber
    )
    
    # Return the consolidated customer information
    return customer_response