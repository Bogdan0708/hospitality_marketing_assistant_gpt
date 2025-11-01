FROM python:3.11-slim

WORKDIR /app

COPY libs/common /opt/libs/common
RUN pip install --no-cache-dir fastapi uvicorn[standard] httpx \\
    && pip install --no-cache-dir -e /opt/libs/common

COPY ui/api-gateway/main.py ./main.py

ENV PYTHONPATH=/app:/opt/libs

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
