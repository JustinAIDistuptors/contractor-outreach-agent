"""
Helper utilities for the Contractor Outreach Agent
"""

import re
import json
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def validate_email(email):
    """
    Validate an email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """
    Validate a phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove common formatting characters
    clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid format (10+ digits)
    return bool(re.match(r'^\+?[0-9]{10,15}$', clean_phone))

def format_timestamp(timestamp=None):
    """
    Format a timestamp in a consistent way
    
    Args:
        timestamp: Datetime object or ISO format string (default: now)
        
    Returns:
        str: Formatted timestamp
    """
    if timestamp is None:
        dt = datetime.now()
    elif isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp)
    else:
        dt = timestamp
        
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def load_json_file(file_path):
    """
    Load data from a JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        dict: Loaded JSON data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {}

def save_json_file(file_path, data):
    """
    Save data to a JSON file
    
    Args:
        file_path: Path to the JSON file
        data: Data to save
        
    Returns:
        bool: Success status
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False

def extract_emails_from_website(url):
    """
    Extract email addresses from a website
    
    Args:
        url: Website URL
        
    Returns:
        list: List of extracted email addresses
    """
    try:
        # Get website content
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch website content: {response.status_code}")
            return []
            
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        text = soup.get_text()
        
        # Find email addresses using regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        
        # Deduplicate and validate
        valid_emails = []
        seen = set()
        for email in emails:
            if email.lower() not in seen and validate_email(email):
                valid_emails.append(email)
                seen.add(email.lower())
                
        return valid_emails
        
    except Exception as e:
        logger.error(f"Error extracting emails from website: {str(e)}")
        return []

def extract_phone_from_website(url):
    """
    Extract phone numbers from a website
    
    Args:
        url: Website URL
        
    Returns:
        list: List of extracted phone numbers
    """
    try:
        # Get website content
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch website content: {response.status_code}")
            return []
            
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        text = soup.get_text()
        
        # Find phone numbers using regex
        # This pattern looks for various phone number formats
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
            r'\d{3}[-.\s]?\d{4}',  # 456-7890
            r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # +1 123-456-7890
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        # Deduplicate and validate
        valid_phones = []
        seen = set()
        for phone in phones:
            clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
            if clean_phone not in seen and validate_phone(phone):
                valid_phones.append(phone)
                seen.add(clean_phone)
                
        return valid_phones
        
    except Exception as e:
        logger.error(f"Error extracting phone numbers from website: {str(e)}")
        return []

def clean_zip_code(zip_code):
    """
    Clean and validate a ZIP code
    
    Args:
        zip_code: ZIP code to clean
        
    Returns:
        str: Cleaned ZIP code or None if invalid
    """
    # Remove any non-digit characters
    clean = re.sub(r'\D', '', str(zip_code))
    
    # Check if it's a valid 5-digit or 9-digit (ZIP+4) code
    if len(clean) == 5 or len(clean) == 9:
        return clean
    
    return None 