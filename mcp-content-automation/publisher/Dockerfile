FROM python:3.11-slim

WORKDIR /app

COPY libs/common /opt/libs/common
RUN pip install --no-cache-dir fastapi uvicorn[standard] httpx \\
    && pip install --no-cache-dir -e /opt/libs/common

COPY mcp-content-automation/publisher/pyproject.toml ./pyproject.toml
COPY mcp-content-automation/publisher/app ./app

ENV PYTHONPATH=/app:/opt/libs

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
