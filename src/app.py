#!/usr/bin/env python3
"""
Contractor Outreach Agent
Main application entry point
"""

import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "status": "success",
        "message": "Contractor Outreach Agent API is running",
        "version": "0.1.0"
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    })

# Import routes after app is initialized to avoid circular imports
from src.api import webhooks

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    logger.info(f"Starting Contractor Outreach Agent on port {port} in {os.getenv('ENVIRONMENT', 'development')} mode")
    app.run(host="0.0.0.0", port=port, debug=debug) 