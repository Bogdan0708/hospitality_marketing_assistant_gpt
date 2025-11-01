FROM python:3.11-slim

WORKDIR /app

COPY libs/common /opt/libs/common
RUN pip install --no-cache-dir streamlit requests \\
    && pip install --no-cache-dir -e /opt/libs/common

COPY ui/dashboard/app.py ./app.py

ENV PYTHONPATH=/app:/opt/libs

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
