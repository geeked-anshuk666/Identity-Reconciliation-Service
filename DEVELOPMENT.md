# Development Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Virtual environment tool (venv or virtualenv)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd bitespeed-identity-reconciliation
```

### 2. Create a Virtual Environment

```bash
# Using venv (Python 3.3+)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file and modify as needed:

```bash
# On Windows:
copy .env.example .env
# On macOS/Linux:
cp .env.example .env
```

Edit the `.env` file to configure your database URL and other settings.

For development, you can use SQLite:

```
DATABASE_URL=sqlite+aiosqlite:///./bitespeed.db
```

For production with PostgreSQL:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bitespeed
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start the Development Server

```bash
# Using the run script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

## Project Structure

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

## Running Tests

To run the test suite:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=app
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations

### Creating a New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
alembic upgrade head
```

### Rolling Back Migrations

```bash
alembic downgrade -1  # Rollback one migration
```

## Deployment

### Local Deployment

1. Ensure all dependencies are installed
2. Set up environment variables
3. Run database migrations
4. Start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Render Deployment

The project is configured for deployment on Render.com. The `render.yaml` file contains the necessary configuration.

1. Fork the repository to your GitHub account
2. Connect your GitHub repository to Render
3. Render will automatically deploy the application using the configuration in `render.yaml`

Environment variables will be automatically set by Render, including the `DATABASE_URL` for the PostgreSQL database.

## Development Workflow

1. Create a new branch for your feature or bug fix
2. Make your changes
3. Write tests for your changes
4. Run the test suite to ensure everything works
5. Commit your changes with a clear message
6. Push to your fork and create a pull request

## Code Quality

- Follow PEP 8 style guide for Python code
- Use type hints wherever possible
- Write docstrings for all functions and classes
- Keep functions small and focused
- Write unit tests for all business logic

## Troubleshooting

### Common Issues

1. **Module not found errors**: Ensure you've activated your virtual environment and installed dependencies.

2. **Database connection errors**: Check your DATABASE_URL in the .env file.

3. **Alembic migration errors**: Ensure you've run `alembic upgrade head` to apply all migrations.

### Getting Help

If you encounter issues:
1. Check the error messages carefully
2. Review the documentation
3. Search for similar issues online
4. Ask for help in the project's communication channels