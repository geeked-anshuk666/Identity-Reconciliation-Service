import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.identity_service import IdentityService
from app.models.contact import Contact
from datetime import datetime

class TestIdentityService:
    @pytest.mark.asyncio
    async def test_new_customer_creation(self, db_session: AsyncSession):
        """Test creating a new customer profile
        
        When a customer provides contact information that doesn't match any
        existing records, we should create a new primary contact for them.
        """
        service = IdentityService(db_session)
        # Create a new customer with email and phone
        customer_response = await service.identify_contact("test@example.com", "1234567890")
        
        # Verify response contains expected data
        assert customer_response.contact.primaryContatctId is not None
        assert customer_response.contact.emails == ["test@example.com"]
        assert customer_response.contact.phoneNumbers == ["1234567890"]
        assert customer_response.contact.secondaryContactIds == []
        
        # Verify contact was created in database
        contact_record = await db_session.get(Contact, customer_response.contact.primaryContatctId)
        assert contact_record is not None
        assert contact_record.email == "test@example.com"
        assert contact_record.phone_number == "1234567890"
        assert contact_record.link_precedence == "primary"
        
        # Verify timestamps are set
        assert contact_record.created_at is not None
        assert contact_record.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_adding_customer_info(self, db_session: AsyncSession):
        """Test adding new information to an existing customer
        
        When a customer provides partial new information (e.g., same email
        but different phone number), we should add this as a secondary contact.
        """
        # First create a primary contact with email and phone
        service = IdentityService(db_session)
        first_customer_response = await service.identify_contact("test@example.com", "1234567890")
        primary_contact_id = first_customer_response.contact.primaryContatctId
        
        # Now create a secondary contact with same email but different phone
        # This simulates a customer using a different phone number
        second_customer_response = await service.identify_contact("test@example.com", "0987654321")
        
        # Should still return the same primary contact
        assert second_customer_response.contact.primaryContatctId == primary_contact_id
        assert "test@example.com" in second_customer_response.contact.emails
        assert "1234567890" in second_customer_response.contact.phoneNumbers
        assert "0987654321" in second_customer_response.contact.phoneNumbers
        assert len(second_customer_response.contact.secondaryContactIds) == 1
    
    @pytest.mark.asyncio
    async def test_recognizing_existing_customer(self, db_session: AsyncSession):
        """Test recognizing a returning customer
        
        When a customer submits the exact same information they've provided
        before, we should return their existing profile without duplication.
        """
        service = IdentityService(db_session)
        
        # Create a contact with specific email and phone
        result1 = await service.identify_contact("test@example.com", "1234567890")
        primary_id = result1.contact.primaryContatctId
        
        # Send the exact same request again (simulating duplicate submission)
        result2 = await service.identify_contact("test@example.com", "1234567890")
        
        # Should return the same primary contact with no new contacts created
        assert result2.contact.primaryContatctId == primary_id
        assert result2.contact.emails == ["test@example.com"]
        assert result2.contact.phoneNumbers == ["1234567890"]
        assert result2.contact.secondaryContactIds == []
    
    @pytest.mark.asyncio
    async def test_merging_customer_histories(self, db_session: AsyncSession):
        """Test merging separate customer profiles
        
        When we discover that two seemingly different customers are actually
        the same person (matching on different contact methods), we should
        merge their profiles under a single primary contact.
        """
        service = IdentityService(db_session)
        
        # Create first primary contact (customer initially identified by email)
        # This might represent a customer who first signed up with their email
        result1 = await service.identify_contact("first@example.com", "1111111111")
        first_primary_id = result1.contact.primaryContatctId
        
        # Create second primary contact (same customer identified by phone)
        # This might represent the same customer calling customer service
        result2 = await service.identify_contact("second@example.com", "2222222222")
        second_primary_id = result2.contact.primaryContatctId
        
        # Now link them by providing data that matches both
        # This simulates discovering that both contacts are the same person
        # (e.g., customer provides both email and phone in a later interaction)
        result3 = await service.identify_contact("first@example.com", "2222222222")
        
        # The older primary should remain primary (we assume first is older)
        # This preserves the original contact history
        assert result3.contact.primaryContatctId == first_primary_id
        
        # Both email addresses should now be associated with the contact
        assert "first@example.com" in result3.contact.emails
        assert "second@example.com" in result3.contact.emails
        
        # Both phone numbers should now be associated with the contact
        assert "1111111111" in result3.contact.phoneNumbers
        assert "2222222222" in result3.contact.phoneNumbers
        
        # Second primary should now be a secondary (linked to the first)
        assert second_primary_id in result3.contact.secondaryContactIds or \
               len(result3.contact.secondaryContactIds) > 0
    
    @pytest.mark.asyncio
    async def test_customer_with_only_phone(self, db_session: AsyncSession):
        """Test handling customers who only provide a phone number
        
        Some customers may only be willing to provide their phone number,
        and our service should handle this gracefully.
        """
        service = IdentityService(db_session)
        result = await service.identify_contact(None, "1234567890")
        
        assert result.contact.primaryContatctId is not None
        assert result.contact.emails == []
        assert result.contact.phoneNumbers == ["1234567890"]
        assert result.contact.secondaryContactIds == []
    
    @pytest.mark.asyncio
    async def test_customer_with_only_email(self, db_session: AsyncSession):
        """Test handling customers who only provide an email
        
        Some customers may only be willing to provide their email,
        and our service should handle this gracefully.
        """
        service = IdentityService(db_session)
        result = await service.identify_contact("test@example.com", None)
        
        assert result.contact.primaryContatctId is not None
        assert result.contact.emails == ["test@example.com"]
        assert result.contact.phoneNumbers == []
        assert result.contact.secondaryContactIds == []
    
    @pytest.mark.asyncio
    async def test_email_case_insensitivity(self, db_session: AsyncSession):
        """Test handling email case differences
        
        Customers might type their email addresses with different cases,
        but they should still be recognized as the same person.
        """
        service = IdentityService(db_session)
        result1 = await service.identify_contact("TEST@EXAMPLE.COM", "1234567890")
        result2 = await service.identify_contact("test@example.com", "0987654321")
        
        # Should link the contacts because emails are the same (case insensitive)
        assert result1.contact.primaryContatctId == result2.contact.primaryContatctId
        assert "test@example.com" in result2.contact.emails  # Normalized to lowercase
        assert "1234567890" in result2.contact.phoneNumbers
        assert "0987654321" in result2.contact.phoneNumbers