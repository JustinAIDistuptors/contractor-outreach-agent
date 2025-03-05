"""
Outreach Manager Service
Handles sending outreach messages to contractors through various channels
"""

import os
import logging
import smtplib
import anthropic
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from datetime import datetime
from src.services.tracking import TrackingService

logger = logging.getLogger(__name__)

class OutreachManager:
    """Service for managing outreach to contractors"""
    
    def __init__(self):
        """Initialize the outreach manager service"""
        # Initialize email settings
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
        
        # Initialize Twilio settings
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Initialize Anthropic settings
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Initialize tracking service
        self.tracking_service = TrackingService()
        
        # Check if we're in development mode
        self.is_development = os.getenv("ENVIRONMENT", "development").lower() == "development"
        if self.is_development:
            logger.info("Running in development mode - messages will be logged but not sent")
    
    def process_outreach_batch(self, project_id, contractors, project_details, bid_link):
        """
        Process outreach to a batch of contractors
        
        Args:
            project_id: ID of the project
            contractors: List of contractor dictionaries
            project_details: Details of the project
            bid_link: Link to the bid submission page
            
        Returns:
            dict: Summary of outreach results
        """
        results = {
            "total": len(contractors),
            "email_sent": 0,
            "sms_sent": 0,
            "voice_call_sent": 0,
            "failed": 0
        }
        
        for contractor in contractors:
            try:
                # Generate personalized message using AI
                message = self._generate_personalized_message(
                    contractor_name=contractor.get('name', ''),
                    project_type=project_details.split()[0] if project_details else "construction",
                    project_details=project_details
                )
                
                # Track this outreach attempt
                outreach_id = self.tracking_service.create_outreach_record(
                    project_id=project_id,
                    contractor=contractor,
                    message=message,
                    bid_link=bid_link
                )
                
                # Determine which channels to use based on available contact info
                channels_used = []
                
                # Try email if available
                if contractor.get('email'):
                    email_result = self._send_email(
                        to_email=contractor['email'],
                        subject=f"Bid Request: {project_details[:50]}...",
                        message=message,
                        bid_link=bid_link
                    )
                    if email_result:
                        channels_used.append('email')
                        results['email_sent'] += 1
                
                # Try SMS if phone available
                if contractor.get('phone'):
                    sms_result = self._send_sms(
                        to_phone=contractor['phone'],
                        message=f"{message[:140]}... Bid details: {bid_link}"
                    )
                    if sms_result:
                        channels_used.append('sms')
                        results['sms_sent'] += 1
                    
                    # Try voice call if SMS was successful
                    if sms_result and self.anthropic_api_key:
                        voice_result = self._schedule_voice_call(
                            to_phone=contractor['phone'],
                            contractor_name=contractor.get('name', ''),
                            project_details=project_details,
                            bid_link=bid_link
                        )
                        if voice_result:
                            channels_used.append('voice')
                            results['voice_call_sent'] += 1
                
                # Update tracking with channels used
                if channels_used:
                    self.tracking_service.update_outreach_channels(
                        outreach_id=outreach_id,
                        channels=channels_used
                    )
                else:
                    results['failed'] += 1
                    logger.warning(f"No outreach channels available for {contractor.get('name', 'unknown contractor')}")
                    
            except Exception as e:
                results['failed'] += 1
                logger.error(f"Error processing outreach to {contractor.get('name', 'unknown')}: {str(e)}")
        
        return results
    
    def _generate_personalized_message(self, contractor_name, project_type, project_details):
        """Generate a personalized outreach message using AI"""
        try:
            if self.anthropic_api_key and not self.is_development:
                # Use Anthropic Claude to generate personalized message
                client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                
                prompt = f"""
                Generate a professional and friendly outreach message to a contractor named {contractor_name}.
                We're looking for bids on a {project_type} project with these details: {project_details}.
                The message should be brief (2-3 paragraphs), professional, and encourage them to submit a bid.
                Don't include any placeholders or variables - this is the final message that will be sent.
                """
                
                message = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=300,
                    temperature=0.7,
                    system="You are an assistant that writes professional business communications.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return message.content[0].text
            else:
                # Fallback to template message if no API key or in development mode
                return f"""
                Hello {contractor_name},
                
                We're currently accepting bids for a {project_type} project and would like to invite you to submit a proposal. Here are the project details: {project_details}
                
                If you're interested, please click the link in this message to submit your bid. We look forward to potentially working with you.
                
                Thank you,
                The Project Team
                """
                
        except Exception as e:
            logger.error(f"Error generating personalized message: {str(e)}")
            # Fallback to simple template
            return f"Hello {contractor_name}, we're looking for bids on a {project_type} project. Details: {project_details}"
    
    def _send_email(self, to_email, subject, message, bid_link):
        """Send an email to a contractor"""
        if self.is_development:
            logger.info(f"[DEV MODE] Would send email to {to_email}: {subject}")
            return True
            
        if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.from_email]):
            logger.warning("Email configuration incomplete - skipping email send")
            return False
            
        try:
            # Create message
            email = MIMEMultipart()
            email['From'] = self.from_email
            email['To'] = to_email
            email['Subject'] = subject
            
            # Add text body
            email.attach(MIMEText(f"{message}\n\nSubmit your bid here: {bid_link}", 'plain'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(email)
                
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def _send_sms(self, to_phone, message):
        """Send an SMS to a contractor"""
        if self.is_development:
            logger.info(f"[DEV MODE] Would send SMS to {to_phone}: {message[:50]}...")
            return True
            
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
            logger.warning("Twilio configuration incomplete - skipping SMS send")
            return False
            
        try:
            # Clean phone number - remove spaces, dashes, etc.
            clean_phone = to_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Add country code if missing
            if not clean_phone.startswith('+'):
                clean_phone = '+1' + clean_phone  # Assuming US number
                
            # Initialize Twilio client
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            # Send message
            sms = client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=clean_phone
            )
            
            logger.info(f"SMS sent to {to_phone} (SID: {sms.sid})")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS to {to_phone}: {str(e)}")
            return False
    
    def _schedule_voice_call(self, to_phone, contractor_name, project_details, bid_link):
        """Schedule an AI voice call to a contractor"""
        if self.is_development:
            logger.info(f"[DEV MODE] Would schedule voice call to {to_phone} for {contractor_name}")
            return True
            
        # This is a placeholder for actual voice call implementation
        # In a real implementation, this would use Twilio or another service
        # to schedule and make an AI-powered voice call
        
        logger.info(f"Voice call scheduling not implemented yet - would call {to_phone}")
        return False 