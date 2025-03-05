#!/usr/bin/env python3
"""
Contractor Outreach Agent
Main application entry point
"""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "status": "success",
        "message": "Contractor Outreach Agent API is running"
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "0.1.0"
    })

# Import routes after app is initialized to avoid circular imports
from src.api import routes

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    app.run(host="0.0.0.0", port=port, debug=debug) 