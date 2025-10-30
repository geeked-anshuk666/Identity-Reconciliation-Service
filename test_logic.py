"""
Simple test to verify our core identity reconciliation logic works
without requiring all the complex dependencies.
"""

from datetime import datetime
from typing import Optional, List

class Contact:
    def __init__(self, id: int, email: Optional[str] = None, phone_number: Optional[str] = None, 
                 linked_id: Optional[int] = None, link_precedence: str = "primary"):
        self.id = id
        self.email = email.lower() if email else None  # Normalize to lowercase
        self.phone_number = phone_number
        self.linked_id = linked_id
        self.link_precedence = link_precedence
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.deleted_at = None
        self.secondary_contacts = []

class IdentityService:
    def __init__(self):
        self.contacts = []
        self.next_id = 1
    
    def find_matching_contacts(self, email: Optional[str], phone_number: Optional[str]) -> List[Contact]:
        """Find contacts by email or phone"""
        if not email and not phone_number:
            return []
            
        # Normalize email to lowercase
        if email:
            email = email.lower()
            
        matches = []
        for contact in self.contacts:
            if contact.deleted_at is None:
                if (email and contact.email == email) or (phone_number and contact.phone_number == phone_number):
                    matches.append(contact)
        return matches
    
    def check_exact_match(self, contacts: List[Contact], email: Optional[str], phone_number: Optional[str]) -> Optional[Contact]:
        """Check if both email and phone match the same contact"""
        if not email or not phone_number:
            return None
            
        # Normalize email to lowercase
        email = email.lower()
            
        for contact in contacts:
            if contact.email == email and contact.phone_number == phone_number:
                return contact
        return None
    
    def create_primary_contact(self, email: Optional[str], phone_number: Optional[str]) -> Contact:
        """Create a new primary contact when no matches found"""
        # Normalize email to lowercase
        if email:
            email = email.lower()
            
        primary_contact = Contact(
            id=self.next_id,
            email=email,
            phone_number=phone_number,
            link_precedence="primary"
        )
        self.next_id += 1
        self.contacts.append(primary_contact)
        return primary_contact
    
    def create_secondary_contact(self, email: Optional[str], phone_number: Optional[str], primary_id: int) -> Contact:
        """Create a secondary contact linked to a primary"""
        # Normalize email to lowercase
        if email:
            email = email.lower()
            
        secondary_contact = Contact(
            id=self.next_id,
            email=email,
            phone_number=phone_number,
            linked_id=primary_id,
            link_precedence="secondary"
        )
        self.next_id += 1
        self.contacts.append(secondary_contact)
        
        # Add to primary's secondary contacts
        primary = self.get_primary_contact(primary_id)
        if primary:
            primary.secondary_contacts.append(secondary_contact)
            
        return secondary_contact
    
    def get_primary_contact(self, contact_id: int) -> Optional[Contact]:
        """Get the primary contact from any contact ID"""
        contact = None
        for c in self.contacts:
            if c.id == contact_id:
                contact = c
                break
                
        if not contact:
            return None
            
        # If contact is already primary, return it
        if contact.link_precedence == "primary":
            return contact
            
        # Otherwise follow linked_id to find primary
        current = contact
        while current.linked_id is not None:
            next_contact = None
            for c in self.contacts:
                if c.id == current.linked_id:
                    next_contact = c
                    break
            if not next_contact:
                return None
            current = next_contact
                
        return current
    
    def handle_partial_match(self, existing_contact: Contact, email: Optional[str], phone_number: Optional[str]) -> Contact:
        """Handle case where email OR phone matches, but not both"""
        # Get the primary contact (in case existing_contact is secondary)
        primary_contact = self.get_primary_contact(existing_contact.id)
        if not primary_contact:
            primary_contact = existing_contact
            
        # Check if new information is truly new
        has_email = email and email.lower() != primary_contact.email
        has_phone = phone_number and phone_number != primary_contact.phone_number
        
        # Check secondary contacts for existing info
        existing_emails = {primary_contact.email} if primary_contact.email else set()
        existing_phones = {primary_contact.phone_number} if primary_contact.phone_number else set()
        
        for secondary in primary_contact.secondary_contacts:
            if secondary.email:
                existing_emails.add(secondary.email)
            if secondary.phone_number:
                existing_phones.add(secondary.phone_number)
        
        # If new info, create secondary contact
        if (has_email and email.lower() not in existing_emails) or (has_phone and phone_number not in existing_phones):
            self.create_secondary_contact(email, phone_number, primary_contact.id)
            
        return primary_contact
    
    def link_primary_contacts(self, email_primary: Contact, phone_primary: Contact) -> Contact:
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
        newer_primary.updated_at = datetime.now()
        
        # Update ALL contacts linked to newer primary to link to older primary
        for secondary in newer_primary.secondary_contacts:
            secondary.linked_id = older_primary.id
            secondary.updated_at = datetime.now()
            
        # Move newer primary's secondaries to older primary
        for secondary in newer_primary.secondary_contacts:
            older_primary.secondary_contacts.append(secondary)
            
        # Clear newer primary's secondaries
        newer_primary.secondary_contacts.clear()
        
        # Add the newer primary as a secondary to the older primary
        older_primary.secondary_contacts.append(newer_primary)
        
        return older_primary
    
    def get_consolidated_contact(self, primary_id: int) -> dict:
        """Build consolidated response for a primary contact"""
        # Find primary contact
        primary_contact = None
        for contact in self.contacts:
            if contact.id == primary_id:
                primary_contact = contact
                break
                
        if not primary_contact:
            raise ValueError("Primary contact not found")
            
        secondary_contacts = primary_contact.secondary_contacts
        
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
        
        return {
            "primaryContatctId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phone_numbers,
            "secondaryContactIds": secondary_contact_ids
        }
    
    def identify_contact(self, email: Optional[str], phone_number: Optional[str]) -> dict:
        """
        Main entry point for identity reconciliation.
        """
        # Validate at least one field is provided
        if not email and not phone_number:
            raise ValueError('At least one of email or phoneNumber must be provided')
            
        # Normalize email to lowercase
        if email:
            email = email.lower()
            
        # Find matching contacts
        matching_contacts = self.find_matching_contacts(email, phone_number)
        
        # Scenario A: No existing contacts
        if not matching_contacts:
            primary_contact = self.create_primary_contact(email, phone_number)
        else:
            # Check if we have an exact match (both email and phone match the same contact)
            exact_match = self.check_exact_match(matching_contacts, email, phone_number)
            
            if exact_match:
                # Scenario C: Exact match
                primary_contact = self.get_primary_contact(exact_match.id)
            else:
                # Check if we have matches for both email and phone but to different primaries
                email_matches = [c for c in matching_contacts if c.email == email]
                phone_matches = [c for c in matching_contacts if c.phone_number == phone_number]
                
                if email_matches and phone_matches:
                    email_primary = self.get_primary_contact(email_matches[0].id)
                    phone_primary = self.get_primary_contact(phone_matches[0].id)
                    
                    if email_primary and phone_primary and email_primary.id != phone_primary.id:
                        # Scenario D: Link two separate primary contacts
                        primary_contact = self.link_primary_contacts(email_primary, phone_primary)
                        
                        # Create a new secondary contact if we have new info
                        if email and phone_number:
                            primary_obj = self.get_primary_contact(primary_contact.id)
                            if primary_obj:
                                existing_emails = {primary_obj.email} if primary_obj.email else set()
                                existing_phones = {primary_obj.phone_number} if primary_obj.phone_number else set()
                                
                                # Collect all existing emails and phones from secondary contacts
                                for secondary in primary_obj.secondary_contacts:
                                    if secondary.email:
                                        existing_emails.add(secondary.email)
                                    if secondary.phone_number:
                                        existing_phones.add(secondary.phone_number)
                                        
                                # Check if we need to create a new secondary contact
                                if email not in existing_emails or phone_number not in existing_phones:
                                    self.create_secondary_contact(email, phone_number, primary_contact.id)
                    else:
                        # Scenario B: Partial match (one field matches)
                        existing_contact = matching_contacts[0]
                        primary_contact = self.handle_partial_match(existing_contact, email, phone_number)
                else:
                    # Scenario B: Partial match (one field matches)
                    existing_contact = matching_contacts[0]
                    primary_contact = self.handle_partial_match(existing_contact, email, phone_number)
        
        # Get consolidated contact information
        if primary_contact:
            consolidated_contact = self.get_consolidated_contact(primary_contact.id)
            return {"contact": consolidated_contact}
        else:
            raise ValueError("Failed to create or find primary contact")

# Test the implementation
def test_identity_service():
    service = IdentityService()
    
    print("=== Test Scenario A: No Existing Contacts ===")
    result = service.identify_contact("lorraine@hillvalley.edu", "123456")
    print(f"Result: {result}")
    print()
    
    print("=== Test Scenario B: Partial Match (Same Phone, Different Email) ===")
    result = service.identify_contact("mcfly@hillvalley.edu", "123456")
    print(f"Result: {result}")
    print()
    
    print("=== Test Scenario C: Exact Match ===")
    result = service.identify_contact("lorraine@hillvalley.edu", "123456")
    print(f"Result: {result}")
    print()
    
    print("=== Test Scenario D: Link Two Separate Primary Contacts ===")
    # Create another primary contact
    result = service.identify_contact("doc@hillvalley.edu", "717171")
    print(f"Created second primary: {result}")
    
    # Now link them by providing data that matches both
    result = service.identify_contact("lorraine@hillvalley.edu", "717171")
    print(f"Linked result: {result}")
    print()
    
    print("=== Test Edge Case: Only Email ===")
    result = service.identify_contact("dave@hillvalley.edu", None)
    print(f"Result: {result}")
    print()
    
    print("=== Test Edge Case: Only Phone ===")
    result = service.identify_contact(None, "999999")
    print(f"Result: {result}")
    print()
    
    print("=== Test Edge Case: Case Insensitive Email ===")
    result = service.identify_contact("LORRAINE@HILLVALLEY.EDU", "111111")
    print(f"Result: {result}")
    print()

if __name__ == "__main__":
    test_identity_service()