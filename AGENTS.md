# Agent Guidelines for Mitch AI Monorepo

## Build/Test/Lint Commands
- **Build all services**: `docker compose up --build`
- **Run single service**: `docker compose up <service-name>`
- **Run tests**: `python -m pytest` (when tests are added)
- **Run single test**: `python -m pytest path/to/test_file.py::test_function`
- **Lint code**: `ruff check .` (when ruff is configured)
- **Format code**: `ruff format .` (when ruff is configured)

## Code Style Guidelines

### Python Standards
- Use Python 3.11+ with `from __future__ import annotations`
- Type hints required for all function parameters and return values
- Use Pydantic BaseModel for all data transfer objects
- Follow FastAPI patterns for API endpoints

### Imports
- Standard library imports first
- Third-party imports second (fastapi, pydantic, sqlalchemy)
- Local imports last with relative imports (from .deps import ...)
- Use explicit imports, avoid wildcard imports

### Naming Conventions
- Functions: snake_case (get_user_data)
- Classes: PascalCase (UserService)
- Variables: snake_case (user_count)
- Constants: UPPER_SNAKE_CASE (MAX_RETRIES)

### Error Handling
- Use HTTPException for API errors with appropriate status codes
- Include descriptive error messages
- Use try/except blocks for database operations with rollback on failure
- Log exceptions with context for debugging

### Database
- Use SQLAlchemy ORM with proper session management
- Implement database migrations when schema changes
- Use connection pooling and proper transaction handling
- Validate data before database operations

### Docker
- Each service should have its own Dockerfile
- Use multi-stage builds for production images
- Expose single port (8000) per service
- Include health checks in docker-compose.yml