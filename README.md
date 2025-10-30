# Bitespeed Identity Reconciliation Service

A web service that tracks and consolidates customer identities across multiple purchases by linking contact information (email and phone numbers).

## Technical Stack

- **Backend Framework**: FastAPI with Python 3.10+
- **Database**: PostgreSQL (production) or SQLite (development)
- **ORM**: SQLAlchemy 2.0 with async support
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Hosting**: Render.com

## Project Structure

```
bitespeed-identity-reconciliation/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and environment variables
│   ├── database.py             # Database connection and session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── contact.py          # SQLAlchemy Contact model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request.py          # Pydantic request schemas
│   │   └── response.py         # Pydantic response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── identity_service.py # Core business logic
│   └── api/
│       ├── __init__.py
│       └── routes.py           # API endpoints
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_identity.py
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── README.md
└── render.yaml                 # Render deployment configuration
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bitespeed-identity-reconciliation
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Copy `.env.example` to `.env` and configure your database URL:
   ```bash
   cp .env.example .env
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### POST /identify

Consolidates customer contact information based on email and phone number.

**Request:**
```json
{
  "email": "string | null",
  "phoneNumber": "string | null"
}
```

**Response:**
```json
{
  "contact": {
    "primaryContatctId": number,
    "emails": string[],
    "phoneNumbers": string[],
    "secondaryContactIds": number[]
  }
}
```

## Example Usage

```bash
# Create first contact
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"email":"lorraine@hillvalley.edu","phoneNumber":"123456"}'

# Create secondary contact
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"email":"mcfly@hillvalley.edu","phoneNumber":"123456"}'

# Link two primary contacts
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"email":"george@hillvalley.edu","phoneNumber":"717171"}'
```

## Running Tests

```bash
pytest
```

## Deployment

The service is configured for deployment on Render.com. The `render.yaml` file contains the necessary configuration.