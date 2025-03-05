"""
Helper utilities for the Contractor Outreach Agent
"""

import re
import json
import logging
from datetime import datetime

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