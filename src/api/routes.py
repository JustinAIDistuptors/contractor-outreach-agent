"""
API Routes for the Contractor Outreach Agent
"""

from flask import jsonify, request
from src.app import app
from src.services.outreach_service import OutreachService

# Initialize services
outreach_service = OutreachService()

@app.route('/api/contractors', methods=['GET'])
def get_contractors():
    """Get all contractors"""
    # This is a placeholder - will be implemented with actual data source
    contractors = [
        {"id": 1, "name": "ABC Construction", "phone": "555-123-4567", "email": "contact@abcconstruction.com"},
        {"id": 2, "name": "XYZ Plumbing", "phone": "555-987-6543", "email": "info@xyzplumbing.com"}
    ]
    return jsonify({"contractors": contractors})

@app.route('/api/outreach', methods=['POST'])
def send_outreach():
    """Send outreach to a contractor"""
    data = request.json
    
    if not data or 'contractor_id' not in data or 'message' not in data:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Placeholder for actual implementation
    result = outreach_service.send_outreach(data['contractor_id'], data['message'])
    
    return jsonify({
        "status": "success",
        "message": f"Outreach sent to contractor {data['contractor_id']}",
        "result": result
    })

@app.route('/api/outreach/<int:contractor_id>', methods=['GET'])
def get_outreach_history(contractor_id):
    """Get outreach history for a contractor"""
    # Placeholder for actual implementation
    history = outreach_service.get_outreach_history(contractor_id)
    
    return jsonify({
        "status": "success",
        "contractor_id": contractor_id,
        "history": history
    }) 