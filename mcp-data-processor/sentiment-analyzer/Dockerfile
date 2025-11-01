FROM python:3.11-slim

WORKDIR /app

COPY mcp-data-processor/sentiment-analyzer/pyproject.toml ./pyproject.toml

RUN pip install --no-cache-dir . --index-url https://download.pytorch.org/whl/cpu

COPY libs/common /opt/libs/common
RUN pip install --no-cache-dir -e /opt/libs/common

COPY mcp-data-processor/sentiment-analyzer/app ./app

ENV PYTHONPATH=/app:/opt/libs

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
