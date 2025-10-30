# Quick Start Guide

## Running the Identity Reconciliation Service

This guide provides multiple ways to run the Bitespeed Identity Reconciliation Service depending on your environment and requirements.

## Option 1: Logic Verification Only (No Dependencies Required)

If you just want to verify the core logic works correctly:

```bash
python test_logic.py
```

This will run all test scenarios and show the output. This approach doesn't require any external dependencies.

## Option 2: Full FastAPI Application (Recommended)

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bitespeed-identity-reconciliation
   ```

2. **Create a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn sqlalchemy alembic aiosqlite pydantic python-dotenv
   ```

4. **Set up environment variables**
   ```bash
   # On Windows
   copy .env.example .env
   
   # On macOS/Linux
   cp .env.example .env
   ```
   
   Edit the `.env` file and make sure it contains:
   ```
   DATABASE_URL=sqlite+aiosqlite:///./bitespeed.db
   APP_ENV=development
   DEBUG=True
   HOST=127.0.0.1
   PORT=8000
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   Or use the provided startup scripts:
   - Windows: `start.bat`
   - macOS/Linux: `start.sh`

7. **Access the application**
   - API: http://127.0.0.1:8000
   - API Documentation: http://127.0.0.1:8000/docs

## Option 3: Using Docker (When Available)

A Dockerfile will be provided in future versions for containerized deployment.

## API Testing

### Using cURL

```bash
# Create first contact
curl -X POST http://127.0.0.1:8000/api/identify \
  -H "Content-Type: application/json" \
  -d '{"email":"lorraine@hillvalley.edu","phoneNumber":"123456"}'

# Create secondary contact
curl -X POST http://127.0.0.1:8000/api/identify \
  -H "Content-Type: application/json" \
  -d '{"email":"mcfly@hillvalley.edu","phoneNumber":"123456"}'

# Link two primary contacts
curl -X POST http://127.0.0.1:8000/api/identify \
  -H "Content-Type: application/json" \
  -d '{"email":"george@hillvalley.edu","phoneNumber":"717171"}'
```

### Using Postman

Import the provided Postman collection:
- File: `Bitespeed_Identity_Reconciliation.postman_collection.json`

## Troubleshooting

### Common Issues

1. **Module not found errors**: Ensure you've activated your virtual environment and installed dependencies.

2. **Database connection errors**: Check your DATABASE_URL in the .env file.

3. **Alembic migration errors**: Ensure you've run `alembic upgrade head` to apply all migrations.

4. **Port already in use**: Change the PORT in .env file or stop the process using the port.

### Python Version Issues

If you encounter issues with Python versions:
1. Make sure you're using Python 3.8 or higher
2. Create a fresh virtual environment
3. Reinstall dependencies

### Windows-Specific Issues

If you encounter issues on Windows:
1. Use PowerShell rather than Command Prompt
2. Ensure you're running the terminal as an administrator if needed
3. Check Windows Defender or antivirus software that might block file access

## Development

To run tests:
```bash
pytest
```

To run tests with coverage:
```bash
pytest --cov=app
```

## Deployment

For production deployment on Render.com:
1. Fork the repository to your GitHub account
2. Connect your GitHub repository to Render
3. Render will automatically deploy using the configuration in `render.yaml`

Environment variables will be automatically set by Render.