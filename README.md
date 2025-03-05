# Contractor Outreach Agent

An AI-powered agent that automates contractor discovery and outreach for bid requests.

## Overview

This service automatically:

1. Finds local contractors based on project type and zip code
2. Extracts contact information through web scraping
3. Sends personalized outreach through multiple channels:
   - Email
   - SMS
   - AI voice calls
4. Tracks responses and engagement
5. Reports results back to the main application

## Project Structure

```
contractor-outreach-agent/
├── config/               # Configuration files
├── data/                 # Data storage
├── src/                  # Source code
│   ├── api/              # API routes
│   │   └── webhooks.py   # Webhook handlers
│   ├── services/         # Core services
│   │   ├── contractor_finder.py  # Find contractors
│   │   ├── outreach_manager.py   # Handle outreach
│   │   └── tracking.py           # Track responses
│   ├── utils/            # Utility functions
│   └── app.py            # Main application
├── tests/                # Test suite
├── .env.example          # Example environment variables
├── requirements.txt      # Python dependencies
└── README.md             # Documentation
```

## Setup

### Prerequisites

- Python 3.8+
- API keys for:
  - Google Places API
  - Twilio
  - Anthropic (Claude)
- SMTP server for email sending

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/JustinAIDistuptors/contractor-outreach-agent.git
   cd contractor-outreach-agent
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration (use `.env.example` as a template):
   ```
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

## Usage

### Starting the Service

Run the application:

```
python src/app.py
```

The service will start on port 5000 (or the port specified in your environment variables).

### Integration with Main App

The agent exposes a webhook endpoint that your main application can call:

```
POST /webhook/bid-request
```

Example request payload:

```json
{
  "project_id": "12345",
  "zip_code": "90210",
  "project_type": "pool installation",
  "project_details": "Looking for a contractor to install a 20x40 in-ground pool with spa.",
  "bid_link": "https://yourapp.com/bids/12345/submit"
}
```

The agent will process this request, find contractors, send outreach, and return results.

### Checking Outreach Status

You can check the status of outreach for a specific project:

```
GET /outreach/status/{project_id}
```

## Development

### Testing

Run tests:

```
pytest
```

### Local Development

For local development without sending actual messages:

1. Set `ENVIRONMENT=development` in your `.env` file
2. Messages will be logged but not actually sent

## Deployment

### Docker

A Dockerfile is provided for containerization:

```
docker build -t contractor-outreach-agent .
docker run -p 5000:5000 --env-file .env contractor-outreach-agent
```

### Cloud Deployment

The service can be deployed to:
- AWS Lambda or EC2
- Google Cloud Run or App Engine
- Heroku

## Extending

### Adding New Outreach Channels

To add a new outreach channel:

1. Add a new method to the `OutreachManager` class in `src/services/outreach_manager.py`
2. Update the `process_outreach_batch` method to include the new channel
3. Add tracking for the new channel in `src/services/tracking.py`

### Adding New Contractor Sources

To add a new source for finding contractors:

1. Add a new method to the `ContractorFinder` class in `src/services/contractor_finder.py`
2. Update the `find_contractors` method to include the new source

## License

[Add license information here] 