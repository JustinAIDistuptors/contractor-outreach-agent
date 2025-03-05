"""
Tests for the ContractorFinder service
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from src.services.contractor_finder import ContractorFinder

@pytest.fixture
def contractor_finder():
    """Create a ContractorFinder instance for testing"""
    with patch.dict(os.environ, {"GOOGLE_PLACES_API_KEY": "test_api_key"}):
        return ContractorFinder()

def test_contractor_finder_initialization():
    """Test that the contractor finder initializes correctly"""
    # Test with no API key
    with patch.dict(os.environ, {}, clear=True):
        finder = ContractorFinder()
        assert finder is not None
        assert finder.google_api_key is None
    
    # Test with API key
    with patch.dict(os.environ, {"GOOGLE_PLACES_API_KEY": "test_api_key"}):
        finder = ContractorFinder()
        assert finder is not None
        assert finder.google_api_key == "test_api_key"

def test_deduplicate_contractors():
    """Test deduplication of contractors"""
    finder = ContractorFinder()
    
    # Test with duplicate names
    contractors = [
        {"name": "ABC Construction", "phone": "123-456-7890", "email": "info@abc.com"},
        {"name": "ABC Construction", "phone": "987-654-3210", "email": "contact@abc.com"},
        {"name": "XYZ Plumbing", "phone": "555-123-4567", "email": "info@xyz.com"}
    ]
    
    unique = finder._deduplicate_contractors(contractors)
    assert len(unique) == 2
    
    # Test with duplicate phones
    contractors = [
        {"name": "ABC Construction", "phone": "123-456-7890", "email": "info@abc.com"},
        {"name": "DEF Builders", "phone": "123-456-7890", "email": "info@def.com"},
        {"name": "XYZ Plumbing", "phone": "555-123-4567", "email": "info@xyz.com"}
    ]
    
    unique = finder._deduplicate_contractors(contractors)
    assert len(unique) == 2
    
    # Test with duplicate emails
    contractors = [
        {"name": "ABC Construction", "phone": "123-456-7890", "email": "info@abc.com"},
        {"name": "DEF Builders", "phone": "987-654-3210", "email": "info@abc.com"},
        {"name": "XYZ Plumbing", "phone": "555-123-4567", "email": "info@xyz.com"}
    ]
    
    unique = finder._deduplicate_contractors(contractors)
    assert len(unique) == 2

@patch('src.services.contractor_finder.requests.get')
def test_find_from_google_places(mock_get, contractor_finder):
    """Test finding contractors from Google Places API"""
    # Mock the geocoding response
    geocode_response = MagicMock()
    geocode_response.json.return_value = {
        "status": "OK",
        "results": [
            {
                "geometry": {
                    "location": {
                        "lat": 34.0522,
                        "lng": -118.2437
                    }
                }
            }
        ]
    }
    
    # Mock the places response
    places_response = MagicMock()
    places_response.json.return_value = {
        "status": "OK",
        "results": [
            {
                "place_id": "place123",
                "name": "ABC Construction",
                "rating": 4.5
            },
            {
                "place_id": "place456",
                "name": "XYZ Plumbing",
                "rating": 4.0
            }
        ]
    }
    
    # Mock the place details responses
    details_response1 = MagicMock()
    details_response1.json.return_value = {
        "status": "OK",
        "result": {
            "formatted_address": "123 Main St, Los Angeles, CA 90001",
            "formatted_phone_number": "123-456-7890",
            "website": "https://abc-construction.com"
        }
    }
    
    details_response2 = MagicMock()
    details_response2.json.return_value = {
        "status": "OK",
        "result": {
            "formatted_address": "456 Oak St, Los Angeles, CA 90001",
            "formatted_phone_number": "987-654-3210",
            "website": "https://xyz-plumbing.com"
        }
    }
    
    # Set up the mock to return different responses for different URLs
    def mock_get_side_effect(url, *args, **kwargs):
        if "geocode" in url:
            return geocode_response
        elif "nearbysearch" in url:
            return places_response
        elif "place123" in url:
            return details_response1
        elif "place456" in url:
            return details_response2
        return MagicMock()
    
    mock_get.side_effect = mock_get_side_effect
    
    # Call the method
    contractors = contractor_finder._find_from_google_places("plumbing", "90001")
    
    # Verify results
    assert len(contractors) == 2
    assert contractors[0]["name"] == "ABC Construction"
    assert contractors[0]["phone"] == "123-456-7890"
    assert contractors[0]["website"] == "https://abc-construction.com"
    assert contractors[1]["name"] == "XYZ Plumbing"
    assert contractors[1]["phone"] == "987-654-3210"
    assert contractors[1]["website"] == "https://xyz-plumbing.com"

def test_find_contractors_integration(contractor_finder):
    """Integration test for find_contractors method"""
    # Mock the underlying methods
    with patch.object(contractor_finder, '_find_from_google_places') as mock_google, \
         patch.object(contractor_finder, '_find_from_web_scraping') as mock_scraping:
        
        # Set up mock return values
        mock_google.return_value = [
            {"name": "ABC Construction", "phone": "123-456-7890", "email": "", "source": "google_places"},
            {"name": "XYZ Plumbing", "phone": "987-654-3210", "email": "", "source": "google_places"}
        ]
        
        mock_scraping.return_value = [
            {"name": "DEF Builders", "phone": "555-123-4567", "email": "info@def.com", "source": "web_scraping"},
            {"name": "ABC Construction", "phone": "123-456-7890", "email": "info@abc.com", "source": "web_scraping"}
        ]
        
        # Call the method
        contractors = contractor_finder.find_contractors("plumbing", "90001", max_results=3)
        
        # Verify results
        assert len(contractors) == 3  # Should be 3 unique contractors
        assert mock_google.called
        assert mock_scraping.called
        
        # Verify sources
        sources = [c["source"] for c in contractors]
        assert "google_places" in sources
        assert "web_scraping" in sources 