FROM python:3.11-slim

WORKDIR /app

COPY mcp-data-processor/trend-detector/pyproject.toml ./pyproject.toml

RUN pip install --no-cache-dir .

COPY libs/common /opt/libs/common
RUN pip install --no-cache-dir -e /opt/libs/common

COPY mcp-data-processor/trend-detector/app ./app

ENV PYTHONPATH=/app:/opt/libs

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
