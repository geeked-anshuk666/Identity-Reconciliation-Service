# Development Guide

Hey fellow developer! 👩‍💻👨‍💻 Welcome to the development guide for the Bitespeed Identity Reconciliation Service. Whether you're contributing to the project or just poking around, this guide will help you get set up and understand how everything works.

## What You'll Need

- Python 3.10 or higher
- pip (Python package installer)
- Virtual environment tool (venv works great)

## Getting Set Up

### 1. Grab the Repository

```bash
git clone <repository-url>
cd bitespeed-identity-reconciliation
```

### 2. Virtual Environment (Because It's Clean)

```bash
# Using venv (comes with Python 3.3+)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install the Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Copy the example environment file and tweak it as needed:

```bash
# On Windows:
copy .env.example .env
# On macOS/Linux:
cp .env.example .env
```

Open up the `.env` file and configure your settings.

For development, SQLite works great:
```
DATABASE_URL=sqlite+aiosqlite:///./bitespeed.db
```

For production with PostgreSQL:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bitespeed
```

### 5. Database Migrations

```bash
alembic upgrade head
```

### 6. Start It Up

```bash
# Using the run script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload
```

You'll find the application at `http://localhost:8000`

## How Everything Fits Together

```
bitespeed-identity-reconciliation/
├── app/                      # Main application package
│   ├── api/                  # API routes
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   ├── config.py             # Configuration
│   ├── database.py           # Database connection
│   └── main.py               # FastAPI application
├── alembic/                  # Database migrations
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment file
├── .gitignore               # Git ignore file
├── alembic.ini              # Alembic configuration
├── render.yaml              # Render deployment config
├── run.py                   # Application runner
├── start.bat                # Windows startup script
├── start.sh                 # Unix startup script
└── README.md                # Project documentation
```

## Testing Our Work

To run the test suite:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=app
```

## API Documentation (It's Automatic!)

FastAPI automatically generates interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations (When Things Change)

### Creating a New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
alembic upgrade head
```

### Rolling Back (Oops!)

```bash
alembic downgrade -1  # Rollback one migration
```

## Getting It Live

### Local Deployment

1. Make sure all dependencies are installed
2. Set up environment variables
3. Run database migrations
4. Start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Render Deployment

The project is all set up for deployment on Render.com. The `render.yaml` file has everything Render needs.

1. Fork the repository to your GitHub account
2. Connect your GitHub repository to Render
3. Render will automatically deploy the application using the configuration in `render.yaml`

Environment variables will be automatically set by Render, including the `DATABASE_URL` for the PostgreSQL database.

## Our Development Workflow

Here's how we like to work:

1. Create a new branch for your feature or bug fix
2. Make your changes
3. Write tests for your changes
4. Run the test suite to make sure everything still works
5. Commit your changes with a clear message
6. Push to your fork and create a pull request

## Code Quality (We Care!)

- Follow PEP 8 style guide for Python code
- Use type hints wherever possible (they're helpful!)
- Write docstrings for all functions and classes
- Keep functions small and focused on one thing
- Write unit tests for all business logic

## Troubleshooting (Because It Never Goes Perfectly)

### Common Issues

1. **"Module not found" errors**: Did you activate your virtual environment and install dependencies?

2. **Database connection errors**: Check your DATABASE_URL in the .env file.

3. **Alembic migration errors**: Make sure you ran `alembic upgrade head` to apply all migrations.

### Need Help?

If you're stuck:
1. Check the error messages carefully
2. Review the documentation
3. Search for similar issues online
4. Ask for help in the project's communication channels