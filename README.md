# BloodDeck Backend

This is the Django-based backend for the BloodDeck project.

## Project Structure
* **blooddeck/**: Project configuration and settings (WSGI, ASGI, Settings).
* **api/**: Main application logic, models, and REST API endpoints.

## Setup Instructions

### 1. Environment Setup
Create a virtual environment to keep dependencies isolated:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


pip install -r requirements.txt