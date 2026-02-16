FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY services/api_gateway/requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY services/api_gateway ./
COPY shared ./shared


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
