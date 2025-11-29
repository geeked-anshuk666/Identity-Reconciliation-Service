# Identity Reconciliation Service

Hey there! Welcome to the Identity Reconciliation Service. This nifty little web service helps us track and consolidate customer identities across multiple purchases by smartly linking their contact information (email addresses and phone numbers).

Ever had a customer who signs up with their email, then later calls in with a phone number, and you're not sure if it's the same person? This service solves exactly that problem.

## What's in the Tech Stack

Here's what we're working with:
- **Backend**: FastAPI with Python 3.10+ (it's fast, I promise!)
- **Database**: PostgreSQL for production, SQLite for development
- **ORM**: SQLAlchemy 2.0 with async support (because we like things modern)
- **Migrations**: Alembic (handles database changes like a champ)
- **Validation**: Pydantic v2 (keeps our data clean)
- **Hosting**: Render.com (where we deploy)

## How's This Thing Organized

```
Identity-reconciliation/
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

## Getting This Running

Alright, let's get this party started:

1. **Grab the code**
   ```bash
   git clone <repository-url>
   cd identity-reconciliation
   ```

2. **Set up your virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install what we need**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables time**
   Copy `.env.example` to `.env` and tweak your database URL:
   ```bash
   cp .env.example .env
   ```

5. **Database setup**
   ```bash
   alembic upgrade head
   ```

6. **Fire it up**
   ```bash
   uvicorn app.main:app --reload
   ```

## Talking to the API

### POST /identify

This is our main endpoint. It takes customer contact info and figures out who they are.

**What you send:**
```json
{
  "email": "string | null",
  "phoneNumber": "string | null"
}
```

**What you get back:**
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

## Try It Out

Here are some examples to get you going:

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

## Testing Things Out

```bash
pytest
```

## Getting It Live

The service is all set up for deployment on Render.com. Check out the `render.yaml` file for the specifics.

## Deployment

The service is currently deployed and accessible at:
- **API Root**: https://identity-reconciliation-service-3ay7.onrender.com
- **Swagger UI**: https://identity-reconciliation-service-3ay7.onrender.com/docs

You can use the Swagger UI to test all the API endpoints interactively.
