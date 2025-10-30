import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.identity_service import IdentityService
from app.models.contact import Contact
from datetime import datetime

class TestIdentityService:
    @pytest.mark.asyncio
    async def test_create_new_primary_contact(self, db_session: AsyncSession):
        """Test Scenario A: No Existing Contacts"""
        service = IdentityService(db_session)
        result = await service.identify_contact("test@example.com", "1234567890")
        
        assert result.contact.primaryContatctId is not None
        assert result.contact.emails == ["test@example.com"]
        assert result.contact.phoneNumbers == ["1234567890"]
        assert result.contact.secondaryContactIds == []
        
        # Verify contact was created in database
        contact = await db_session.get(Contact, result.contact.primaryContatctId)
        assert contact is not None
        assert contact.email == "test@example.com"
        assert contact.phone_number == "1234567890"
        assert contact.link_precedence == "primary"
    
    @pytest.mark.asyncio
    async def test_create_secondary_on_partial_match(self, db_session: AsyncSession):
        """Test Scenario B: Partial Match"""
        # First create a primary contact
        service = IdentityService(db_session)
        result1 = await service.identify_contact("test@example.com", "1234567890")
        primary_id = result1.contact.primaryContatctId
        
        # Now create a secondary contact with same email but different phone
        result2 = await service.identify_contact("test@example.com", "0987654321")
        
        # Should still return the same primary
        assert result2.contact.primaryContatctId == primary_id
        assert "test@example.com" in result2.contact.emails
        assert "1234567890" in result2.contact.phoneNumbers
        assert "0987654321" in result2.contact.phoneNumbers
        assert len(result2.contact.secondaryContactIds) == 1
    
    @pytest.mark.asyncio
    async def test_no_duplicate_on_exact_match(self, db_session: AsyncSession):
        """Test Scenario C: Exact Match"""
        service = IdentityService(db_session)
        
        # Create a contact
        result1 = await service.identify_contact("test@example.com", "1234567890")
        primary_id = result1.contact.primaryContatctId
        
        # Send the same request again
        result2 = await service.identify_contact("test@example.com", "1234567890")
        
        # Should return the same primary contact with no new contacts created
        assert result2.contact.primaryContatctId == primary_id
        assert result2.contact.emails == ["test@example.com"]
        assert result2.contact.phoneNumbers == ["1234567890"]
        assert result2.contact.secondaryContactIds == []
    
    @pytest.mark.asyncio
    async def test_link_two_primary_contacts(self, db_session: AsyncSession):
        """Test Scenario D: Link Two Primaries"""
        service = IdentityService(db_session)
        
        # Create first primary contact
        result1 = await service.identify_contact("first@example.com", "1111111111")
        first_primary_id = result1.contact.primaryContatctId
        
        # Create second primary contact
        result2 = await service.identify_contact("second@example.com", "2222222222")
        second_primary_id = result2.contact.primaryContatctId
        
        # Now link them by providing data that matches both
        result3 = await service.identify_contact("first@example.com", "2222222222")
        
        # The older primary should remain primary (we assume first is older)
        assert result3.contact.primaryContatctId == first_primary_id
        assert "first@example.com" in result3.contact.emails
        assert "second@example.com" in result3.contact.emails
        assert "1111111111" in result3.contact.phoneNumbers
        assert "2222222222" in result3.contact.phoneNumbers
        # Second primary should now be a secondary
        assert second_primary_id in result3.contact.secondaryContactIds or \
               len(result3.contact.secondaryContactIds) > 0
    
    @pytest.mark.asyncio
    async def test_null_email(self, db_session: AsyncSession):
        """Test Edge Case: Null Email"""
        service = IdentityService(db_session)
        result = await service.identify_contact(None, "1234567890")
        
        assert result.contact.primaryContatctId is not None
        assert result.contact.emails == []
        assert result.contact.phoneNumbers == ["1234567890"]
        assert result.contact.secondaryContactIds == []
    
    @pytest.mark.asyncio
    async def test_null_phone(self, db_session: AsyncSession):
        """Test Edge Case: Null Phone"""
        service = IdentityService(db_session)
        result = await service.identify_contact("test@example.com", None)
        
        assert result.contact.primaryContatctId is not None
        assert result.contact.emails == ["test@example.com"]
        assert result.contact.phoneNumbers == []
        assert result.contact.secondaryContactIds == []
    
    @pytest.mark.asyncio
    async def test_case_insensitive_email(self, db_session: AsyncSession):
        """Test Edge Case: Case Insensitive Email"""
        service = IdentityService(db_session)
        result1 = await service.identify_contact("TEST@EXAMPLE.COM", "1234567890")
        result2 = await service.identify_contact("test@example.com", "0987654321")
        
        # Should link the contacts because emails are the same (case insensitive)
        assert result1.contact.primaryContatctId == result2.contact.primaryContatctId
        assert "test@example.com" in result2.contact.emails  # Normalized to lowercase
        assert "1234567890" in result2.contact.phoneNumbers
        assert "0987654321" in result2.contact.phoneNumbers