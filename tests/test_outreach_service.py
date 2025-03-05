"""
Tests for the OutreachService
"""

import pytest
from src.services.outreach_service import OutreachService

def test_outreach_service_initialization():
    """Test that the outreach service initializes correctly"""
    service = OutreachService()
    assert service is not None
    assert hasattr(service, 'outreach_history')
    assert isinstance(service.outreach_history, dict)

def test_send_outreach():
    """Test sending an outreach message"""
    service = OutreachService()
    
    contractor_id = 1
    message = "Hello, this is a test message"
    
    result = service.send_outreach(contractor_id, message)
    
    assert result is not None
    assert result['contractor_id'] == contractor_id
    assert result['message'] == message
    assert 'timestamp' in result
    assert result['status'] == 'sent'

def test_get_outreach_history_empty():
    """Test getting outreach history when empty"""
    service = OutreachService()
    
    contractor_id = 999  # Non-existent contractor
    history = service.get_outreach_history(contractor_id)
    
    assert history == []

def test_get_outreach_history_with_data():
    """Test getting outreach history with data"""
    service = OutreachService()
    
    contractor_id = 2
    message1 = "First test message"
    message2 = "Second test message"
    
    # Send two messages
    service.send_outreach(contractor_id, message1)
    service.send_outreach(contractor_id, message2)
    
    # Get history
    history = service.get_outreach_history(contractor_id)
    
    assert len(history) == 2
    assert history[0]['message'] == message1
    assert history[1]['message'] == message2 