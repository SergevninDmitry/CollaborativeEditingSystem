FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY services/document_service/requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY services/document_service ./
COPY shared ./shared

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
