"""
Webhook handlers for the Contractor Outreach Agent
"""

import logging
from flask import request, jsonify
from src.app import app
from src.services.contractor_finder import ContractorFinder
from src.services.outreach_manager import OutreachManager
from src.services.tracking import TrackingService

# Initialize services
logger = logging.getLogger(__name__)
contractor_finder = ContractorFinder()
outreach_manager = OutreachManager()
tracking_service = TrackingService()

@app.route('/webhook/bid-request', methods=['POST'])
def bid_request_webhook():
    """
    Handle incoming bid request webhooks
    
    Expected payload:
    {
        "project_id": "12345",
        "zip_code": "90210",
        "project_type": "pool installation",
        "project_details": "Looking for a contractor to install a 20x40 in-ground pool with spa.",
        "bid_link": "https://yourapp.com/bids/12345/submit"
    }
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['project_id', 'zip_code', 'project_type', 'project_details', 'bid_link']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"Missing required field: {field}"
            }), 400
    
    try:
        # Find contractors matching the project type and location
        logger.info(f"Finding contractors for project {data['project_id']} ({data['project_type']}) in {data['zip_code']}")
        contractors = contractor_finder.find_contractors(
            project_type=data['project_type'],
            zip_code=data['zip_code']
        )
        
        if not contractors:
            return jsonify({
                "status": "warning",
                "message": "No contractors found matching the criteria",
                "project_id": data['project_id']
            }), 200
        
        # Process outreach to the found contractors
        logger.info(f"Sending outreach to {len(contractors)} contractors for project {data['project_id']}")
        outreach_results = outreach_manager.process_outreach_batch(
            project_id=data['project_id'],
            contractors=contractors,
            project_details=data['project_details'],
            bid_link=data['bid_link']
        )
        
        # Return the results
        return jsonify({
            "status": "success",
            "message": f"Outreach initiated to {len(contractors)} contractors",
            "project_id": data['project_id'],
            "contractors_count": len(contractors),
            "outreach_results": outreach_results
        })
        
    except Exception as e:
        logger.error(f"Error processing bid request: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error processing request: {str(e)}",
            "project_id": data.get('project_id', 'unknown')
        }), 500

@app.route('/outreach/status/<project_id>', methods=['GET'])
def outreach_status(project_id):
    """Get the status of outreach for a specific project"""
    try:
        # Get tracking data for the project
        tracking_data = tracking_service.get_project_tracking(project_id)
        
        if not tracking_data:
            return jsonify({
                "status": "warning",
                "message": f"No outreach data found for project {project_id}",
                "project_id": project_id
            }), 404
        
        # Return the tracking data
        return jsonify({
            "status": "success",
            "project_id": project_id,
            "tracking_data": tracking_data
        })
        
    except Exception as e:
        logger.error(f"Error getting outreach status: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error getting outreach status: {str(e)}",
            "project_id": project_id
        }), 500 