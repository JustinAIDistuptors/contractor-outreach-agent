"""
Contractor Finder Service
Handles finding contractors based on project type and location
"""

import os
import logging
import requests
from bs4 import BeautifulSoup
from src.utils.helpers import validate_email, validate_phone

logger = logging.getLogger(__name__)

class ContractorFinder:
    """Service for finding contractors based on project criteria"""
    
    def __init__(self):
        """Initialize the contractor finder service"""
        self.google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.google_api_key:
            logger.warning("Google Places API key not found in environment variables")
    
    def find_contractors(self, project_type, zip_code, max_results=20):
        """
        Find contractors based on project type and zip code
        
        Args:
            project_type: Type of project (e.g., "pool installation")
            zip_code: ZIP code for the project location
            max_results: Maximum number of contractors to return
            
        Returns:
            list: List of contractor information dictionaries
        """
        logger.info(f"Finding contractors for {project_type} in {zip_code}")
        
        # Combine results from multiple sources
        contractors = []
        
        # Get contractors from Google Places API
        google_contractors = self._find_from_google_places(project_type, zip_code)
        if google_contractors:
            contractors.extend(google_contractors)
            
        # Get contractors from web scraping
        scraped_contractors = self._find_from_web_scraping(project_type, zip_code)
        if scraped_contractors:
            contractors.extend(scraped_contractors)
            
        # Deduplicate contractors based on name, phone, or email
        unique_contractors = self._deduplicate_contractors(contractors)
        
        # Limit to max_results
        return unique_contractors[:max_results]
    
    def _find_from_google_places(self, project_type, zip_code):
        """Find contractors using Google Places API"""
        if not self.google_api_key:
            logger.warning("Skipping Google Places search - API key not configured")
            return []
            
        try:
            # Convert zip code to lat/lng using Google Geocoding API
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={self.google_api_key}"
            geocode_response = requests.get(geocode_url)
            geocode_data = geocode_response.json()
            
            if geocode_data['status'] != 'OK':
                logger.error(f"Geocoding error: {geocode_data['status']}")
                return []
                
            location = geocode_data['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            # Search for contractors using Places API
            search_query = f"{project_type} contractors"
            places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=25000&keyword={search_query}&key={self.google_api_key}"
            
            places_response = requests.get(places_url)
            places_data = places_response.json()
            
            if places_data['status'] != 'OK':
                logger.error(f"Places API error: {places_data['status']}")
                return []
                
            # Process results
            contractors = []
            for place in places_data.get('results', []):
                # Get place details to get phone and website
                place_id = place['place_id']
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website&key={self.google_api_key}"
                
                details_response = requests.get(details_url)
                details_data = details_response.json()
                
                if details_data['status'] == 'OK':
                    place_details = details_data['result']
                    
                    contractor = {
                        'name': place['name'],
                        'address': place_details.get('formatted_address', ''),
                        'phone': place_details.get('formatted_phone_number', ''),
                        'website': place_details.get('website', ''),
                        'email': '',  # Not available from Google Places
                        'source': 'google_places',
                        'rating': place.get('rating', 0),
                        'zip_code': zip_code
                    }
                    
                    contractors.append(contractor)
            
            logger.info(f"Found {len(contractors)} contractors from Google Places")
            return contractors
            
        except Exception as e:
            logger.error(f"Error finding contractors from Google Places: {str(e)}")
            return []
    
    def _find_from_web_scraping(self, project_type, zip_code):
        """Find contractors by scraping business directories"""
        try:
            # This is a placeholder for web scraping implementation
            # In a real implementation, this would scrape contractor directories
            # such as HomeAdvisor, Angie's List, Yelp, etc.
            
            # For demonstration purposes, returning an empty list
            logger.info("Web scraping for contractors not implemented yet")
            return []
            
        except Exception as e:
            logger.error(f"Error finding contractors from web scraping: {str(e)}")
            return []
    
    def _deduplicate_contractors(self, contractors):
        """Remove duplicate contractors based on name, phone, or email"""
        unique_contractors = []
        seen_names = set()
        seen_phones = set()
        seen_emails = set()
        
        for contractor in contractors:
            name = contractor.get('name', '').lower()
            phone = contractor.get('phone', '').replace(' ', '').replace('-', '')
            email = contractor.get('email', '').lower()
            
            # Skip if we've seen this contractor before
            if (name and name in seen_names) or \
               (phone and phone in seen_phones) or \
               (email and email in seen_emails):
                continue
                
            # Add to unique list and update seen sets
            unique_contractors.append(contractor)
            if name:
                seen_names.add(name)
            if phone:
                seen_phones.add(phone)
            if email:
                seen_emails.add(email)
        
        return unique_contractors 