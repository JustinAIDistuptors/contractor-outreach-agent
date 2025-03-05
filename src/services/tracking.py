"""
Tracking Service
Handles tracking of outreach activities and responses
"""

import os
import json
import logging
import uuid
from datetime import datetime
import os.path

logger = logging.getLogger(__name__)

class TrackingService:
    """Service for tracking outreach activities and responses"""
    
    def __init__(self):
        """Initialize the tracking service"""
        # In a production environment, this would use a database
        # For this implementation, we'll use JSON files in the data directory
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create outreach and responses directories
        self.outreach_dir = os.path.join(self.data_dir, 'outreach')
        self.responses_dir = os.path.join(self.data_dir, 'responses')
        os.makedirs(self.outreach_dir, exist_ok=True)
        os.makedirs(self.responses_dir, exist_ok=True)
    
    def create_outreach_record(self, project_id, contractor, message, bid_link):
        """
        Create a record of an outreach attempt
        
        Args:
            project_id: ID of the project
            contractor: Contractor information dictionary
            message: Outreach message content
            bid_link: Link to the bid submission page
            
        Returns:
            str: Unique ID for this outreach record
        """
        outreach_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        record = {
            'outreach_id': outreach_id,
            'project_id': project_id,
            'timestamp': timestamp,
            'contractor': contractor,
            'message': message,
            'bid_link': bid_link,
            'channels': [],
            'status': 'pending',
            'responses': []
        }
        
        # Save to file
        self._save_outreach_record(outreach_id, record)
        
        # Update project tracking
        self._update_project_tracking(project_id, outreach_id, contractor)
        
        return outreach_id
    
    def update_outreach_channels(self, outreach_id, channels):
        """
        Update the channels used for an outreach attempt
        
        Args:
            outreach_id: ID of the outreach record
            channels: List of channel names used (email, sms, voice)
            
        Returns:
            bool: Success status
        """
        record = self._load_outreach_record(outreach_id)
        if not record:
            logger.error(f"Outreach record {outreach_id} not found")
            return False
            
        record['channels'] = channels
        record['status'] = 'sent'
        record['last_updated'] = datetime.now().isoformat()
        
        return self._save_outreach_record(outreach_id, record)
    
    def record_response(self, outreach_id, channel, response_type, details=None):
        """
        Record a response to an outreach attempt
        
        Args:
            outreach_id: ID of the outreach record
            channel: Channel the response came through (email, sms, voice, web)
            response_type: Type of response (opened, clicked, replied, submitted, declined)
            details: Additional details about the response
            
        Returns:
            bool: Success status
        """
        record = self._load_outreach_record(outreach_id)
        if not record:
            logger.error(f"Outreach record {outreach_id} not found")
            return False
            
        response = {
            'timestamp': datetime.now().isoformat(),
            'channel': channel,
            'type': response_type,
            'details': details or {}
        }
        
        record['responses'].append(response)
        record['last_updated'] = datetime.now().isoformat()
        
        # Update status based on response type
        if response_type == 'submitted':
            record['status'] = 'bid_submitted'
        elif response_type == 'declined':
            record['status'] = 'declined'
        elif response_type == 'replied' and record['status'] == 'sent':
            record['status'] = 'replied'
            
        return self._save_outreach_record(outreach_id, record)
    
    def get_project_tracking(self, project_id):
        """
        Get tracking data for a specific project
        
        Args:
            project_id: ID of the project
            
        Returns:
            dict: Project tracking data
        """
        project_file = os.path.join(self.data_dir, f'project_{project_id}.json')
        
        if not os.path.exists(project_file):
            logger.warning(f"No tracking data found for project {project_id}")
            return None
            
        try:
            with open(project_file, 'r') as f:
                project_data = json.load(f)
                
            # Enrich with outreach details
            for outreach_id in project_data.get('outreach_ids', []):
                outreach_record = self._load_outreach_record(outreach_id)
                if outreach_record:
                    if 'outreach_details' not in project_data:
                        project_data['outreach_details'] = []
                    project_data['outreach_details'].append(outreach_record)
                    
            return project_data
            
        except Exception as e:
            logger.error(f"Error loading project tracking data: {str(e)}")
            return None
    
    def _save_outreach_record(self, outreach_id, record):
        """Save an outreach record to file"""
        try:
            outreach_file = os.path.join(self.outreach_dir, f'{outreach_id}.json')
            with open(outreach_file, 'w') as f:
                json.dump(record, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving outreach record: {str(e)}")
            return False
    
    def _load_outreach_record(self, outreach_id):
        """Load an outreach record from file"""
        try:
            outreach_file = os.path.join(self.outreach_dir, f'{outreach_id}.json')
            if not os.path.exists(outreach_file):
                return None
                
            with open(outreach_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading outreach record: {str(e)}")
            return None
    
    def _update_project_tracking(self, project_id, outreach_id, contractor):
        """Update the project tracking data"""
        try:
            project_file = os.path.join(self.data_dir, f'project_{project_id}.json')
            
            if os.path.exists(project_file):
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
            else:
                project_data = {
                    'project_id': project_id,
                    'created_at': datetime.now().isoformat(),
                    'outreach_ids': [],
                    'contractors': {}
                }
            
            # Add outreach ID if not already present
            if outreach_id not in project_data['outreach_ids']:
                project_data['outreach_ids'].append(outreach_id)
            
            # Add contractor info if not already present
            contractor_id = contractor.get('id', contractor.get('name', outreach_id))
            if contractor_id not in project_data['contractors']:
                project_data['contractors'][contractor_id] = contractor
            
            # Update last modified timestamp
            project_data['last_updated'] = datetime.now().isoformat()
            
            # Save project data
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error updating project tracking: {str(e)}")
            return False 