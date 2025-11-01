FROM python:3.11-slim

WORKDIR /app

COPY libs/common /opt/libs/common
RUN pip install --no-cache-dir fastapi uvicorn[standard] httpx pydantic-settings psycopg2-binary sqlalchemy python-multipart \\
    && pip install --no-cache-dir -e /opt/libs/common

COPY mcp-social-analytics/instagram-server/pyproject.toml ./pyproject.toml
COPY mcp-social-analytics/instagram-server/app ./app

ENV PYTHONPATH=/app:/opt/libs

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
