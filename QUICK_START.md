# Quick Start Guide

So you want to get the Bitespeed Identity Reconciliation Service up and running quickly? You've come to the right place! Here are a few different ways to get started depending on what you're looking for.

## Option 1: Just Want to See the Logic Work? (No Dependencies Needed)

If you're just curious about whether the core logic actually works:

```bash
python test_logic.py
```

This will run through all our test scenarios and show you the output. Super simple, no external dependencies required.

## Option 2: Full FastAPI Application (Our Recommended Approach)

### What You'll Need First

- Python 3.8 or higher
- pip (Python package installer)

### Let's Get This Going

1. **Get the code**
   ```bash
   git clone <repository-url>
   cd bitespeed-identity-reconciliation
   ```

2. **Virtual environment (keeps things clean)**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the goodies**
   ```bash
   pip install fastapi uvicorn sqlalchemy alembic aiosqlite pydantic python-dotenv
   ```

4. **Environment setup**
   ```bash
   # On Windows
   copy .env.example .env
   
   # On macOS/Linux
   cp .env.example .env
   ```
   
   Open up that `.env` file and make sure it has:
   ```
   DATABASE_URL=sqlite+aiosqlite:///./bitespeed.db
   APP_ENV=development
   DEBUG=True
   HOST=127.0.0.1
   PORT=8000
   ```

5. **Database migrations (don't skip this!)**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   Or if you prefer, use our handy startup scripts:
   - Windows: `start.bat`
   - macOS/Linux: `start.sh`

7. **Check it out**
   - API: http://127.0.0.1:8000
   - API Docs: http://127.0.0.1:8000/docs

## Option 3: Docker (Coming Soon)

We're working on a Dockerfile for containerized deployment. Stay tuned!

## Testing the API

### Using cURL (Everyone's favorite)

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

### Using Postman (If that's your thing)

Import our Postman collection:
- File: `Bitespeed_Identity_Reconciliation.postman_collection.json`

## Oh No, It's Not Working!

### Common Headaches and How to Fix Them

1. **"Module not found" errors**: Did you remember to activate your virtual environment? And install dependencies?

2. **Database connection issues**: Double-check your DATABASE_URL in the .env file.

3. **Alembic migration problems**: Make sure you ran `alembic upgrade head` to apply all migrations.

4. **Port already taken**: Change the PORT in .env or stop whatever's using that port.

### Python Version Woes

If you're having Python version issues:
1. Make sure you're using Python 3.8 or higher
2. Create a fresh virtual environment
3. Reinstall dependencies

### Windows-Specific Quirks

Running into trouble on Windows?
1. Try PowerShell instead of Command Prompt
2. You might need to run the terminal as an administrator
3. Check if Windows Defender is blocking anything

## Development Stuff

To run tests:
```bash
pytest
```

To run tests with coverage:
```bash
pytest --cov=app
```

## Getting It Live

For production deployment on Render.com:
1. Fork the repository to your GitHub account
2. Connect your GitHub repository to Render
3. Render will automatically deploy using the configuration in `render.yaml`

Environment variables will be automatically set by Render.