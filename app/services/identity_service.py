from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contact import Contact
from app.schemas.response import ContactResponse, IdentifyResponse
from typing import Optional, List
from datetime import datetime

class IdentityService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def identify_contact(self, email: Optional[str], phone_number: Optional[str]) -> IdentifyResponse:
        """
        Main entry point for identity reconciliation.
        
        Steps:
        1. Find all matching contacts by email or phone
        2. Determine if new contact creation is needed
        3. Handle linking logic (primary/secondary)
        4. Return consolidated response
        """
        # Normalize email to lowercase for case insensitivity
        if email:
            email = email.lower()
            
        # Find matching contacts
        matching_contacts = await self.find_matching_contacts(email, phone_number)
        
        # Scenario A: No existing contacts
        if not matching_contacts:
            primary_contact = await self.create_primary_contact(email, phone_number)
        else:
            # Check if we have an exact match (both email and phone match the same contact)
            exact_match = await self.check_exact_match(matching_contacts, email, phone_number)
            
            if exact_match:
                # Scenario C: Exact match
                primary_contact = await self.get_primary_contact(exact_match.id)
            else:
                # Check if we have matches for both email and phone but to different primaries
                email_matches = [c for c in matching_contacts if c.email == email]
                phone_matches = [c for c in matching_contacts if c.phone_number == phone_number]
                
                if email_matches and phone_matches and \
                   (await self.get_primary_contact(email_matches[0].id)).id != (await self.get_primary_contact(phone_matches[0].id)).id:
                    # Scenario D: Link two separate primary contacts
                    primary_contact = await self.link_primary_contacts(
                        await self.get_primary_contact(email_matches[0].id),
                        await self.get_primary_contact(phone_matches[0].id)
                    )
                    
                    # Create a new secondary contact if we have new info
                    if email and phone_number:
                        primary_obj = await self.get_primary_contact(primary_contact.id)
                        existing_emails = {primary_obj.email} if primary_obj.email else set()
                        existing_phones = {primary_obj.phone_number} if primary_obj.phone_number else set()
                        
                        # Collect all existing emails and phones from secondary contacts
                        secondary_contacts = await self.get_secondary_contacts(primary_obj.id)
                        for secondary in secondary_contacts:
                            if secondary.email:
                                existing_emails.add(secondary.email)
                            if secondary.phone_number:
                                existing_phones.add(secondary.phone_number)
                                
                        # Check if we need to create a new secondary contact
                        if email not in existing_emails or phone_number not in existing_phones:
                            await self.create_secondary_contact(email, phone_number, primary_contact.id)
                else:
                    # Scenario B: Partial match (one field matches)
                    existing_contact = matching_contacts[0]
                    primary_contact = await self.handle_partial_match(existing_contact, email, phone_number)
        
        # Get consolidated contact information
        consolidated_contact = await self.get_consolidated_contact(primary_contact.id)
        return IdentifyResponse(contact=consolidated_contact)
    
    async def find_matching_contacts(self, email: Optional[str], phone_number: Optional[str]) -> List[Contact]:
        """Find contacts by email or phone"""
        query = select(Contact).where(
            and_(
                Contact.deleted_at.is_(None),
                or_(
                    Contact.email == email if email else False,
                    Contact.phone_number == phone_number if phone_number else False
                )
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def check_exact_match(self, contacts: List[Contact], email: Optional[str], phone_number: Optional[str]) -> Optional[Contact]:
        """Check if both email and phone match the same contact"""
        if not email or not phone_number:
            return None
            
        for contact in contacts:
            if contact.email == email and contact.phone_number == phone_number:
                return contact
        return None
    
    async def create_primary_contact(self, email: Optional[str], phone_number: Optional[str]) -> Contact:
        """Create a new primary contact when no matches found"""
        primary_contact = Contact(
            email=email,
            phone_number=phone_number,
            link_precedence="primary",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(primary_contact)
        await self.db.commit()
        await self.db.refresh(primary_contact)
        return primary_contact
    
    async def create_secondary_contact(self, email: Optional[str], phone_number: Optional[str], primary_id: int) -> Contact:
        """Create a secondary contact linked to a primary"""
        secondary_contact = Contact(
            email=email,
            phone_number=phone_number,
            linked_id=primary_id,
            link_precedence="secondary",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(secondary_contact)
        await self.db.commit()
        await self.db.refresh(secondary_contact)
        return secondary_contact
    
    async def get_primary_contact(self, contact_id: int) -> Contact:
        """Get the primary contact from any contact ID"""
        contact = await self.db.get(Contact, contact_id)
        if not contact:
            raise ValueError("Contact not found")
            
        # If contact is already primary, return it
        if contact.link_precedence == "primary":
            return contact
            
        # Otherwise follow linked_id to find primary
        while contact.linked_id is not None:
            contact = await self.db.get(Contact, contact.linked_id)
            if not contact:
                raise ValueError("Linked contact not found")
                
        return contact
    
    async def get_secondary_contacts(self, primary_id: int) -> List[Contact]:
        """Get all secondary contacts for a primary contact"""
        query = select(Contact).where(
            and_(
                Contact.linked_id == primary_id,
                Contact.link_precedence == "secondary",
                Contact.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def handle_partial_match(self, existing_contact: Contact, email: Optional[str], phone_number: Optional[str]) -> Contact:
        """Handle case where email OR phone matches, but not both"""
        # Get the primary contact (in case existing_contact is secondary)
        primary_contact = await self.get_primary_contact(existing_contact.id)
        
        # Check if new information is truly new
        has_email = email and email != primary_contact.email
        has_phone = phone_number and phone_number != primary_contact.phone_number
        
        # Check secondary contacts for existing info
        existing_emails = {primary_contact.email} if primary_contact.email else set()
        existing_phones = {primary_contact.phone_number} if primary_contact.phone_number else set()
        
        secondary_contacts = await self.get_secondary_contacts(primary_contact.id)
        for secondary in secondary_contacts:
            if secondary.email:
                existing_emails.add(secondary.email)
            if secondary.phone_number:
                existing_phones.add(secondary.phone_number)
        
        # If new info, create secondary contact
        if (has_email and email not in existing_emails) or (has_phone and phone_number not in existing_phones):
            await self.create_secondary_contact(email, phone_number, primary_contact.id)
            
        return primary_contact
    
    async def link_primary_contacts(self, email_primary: Contact, phone_primary: Contact) -> Contact:
        """Handle case where email matches one primary, phone matches another primary"""
        # Identify which primary is older (by created_at)
        if email_primary.created_at <= phone_primary.created_at:
            older_primary = email_primary
            newer_primary = phone_primary
        else:
            older_primary = phone_primary
            newer_primary = email_primary
            
        # Convert newer primary to secondary
        newer_primary.linked_id = older_primary.id
        newer_primary.link_precedence = "secondary"
        newer_primary.updated_at = datetime.utcnow()
        
        # Update ALL contacts linked to newer primary to link to older primary
        secondary_contacts = await self.get_secondary_contacts(newer_primary.id)
        for secondary in secondary_contacts:
            secondary.linked_id = older_primary.id
            secondary.updated_at = datetime.utcnow()
            
        await self.db.commit()
        await self.db.refresh(newer_primary)
        return older_primary
    
    async def get_consolidated_contact(self, primary_id: int) -> ContactResponse:
        """Build consolidated response for a primary contact"""
        # Fetch primary contact
        primary_contact = await self.db.get(Contact, primary_id)
        if not primary_contact:
            raise ValueError("Primary contact not found")
            
        # Fetch all secondary contacts
        secondary_contacts = await self.get_secondary_contacts(primary_id)
        
        # Collect unique emails (primary first, then secondaries by createdAt)
        emails = []
        if primary_contact.email:
            emails.append(primary_contact.email)
            
        for secondary in sorted(secondary_contacts, key=lambda x: x.created_at):
            if secondary.email and secondary.email not in emails:
                emails.append(secondary.email)
        
        # Collect unique phone numbers (primary first, then secondaries by createdAt)
        phone_numbers = []
        if primary_contact.phone_number:
            phone_numbers.append(primary_contact.phone_number)
            
        for secondary in sorted(secondary_contacts, key=lambda x: x.created_at):
            if secondary.phone_number and secondary.phone_number not in phone_numbers:
                phone_numbers.append(secondary.phone_number)
        
        # Collect all secondary IDs
        secondary_contact_ids = [secondary.id for secondary in secondary_contacts]
        
        return ContactResponse(
            primaryContatctId=primary_contact.id,
            emails=emails,
            phoneNumbers=phone_numbers,
            secondaryContactIds=secondary_contact_ids
        )