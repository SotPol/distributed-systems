FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn cassandra-driver pymongo passlib[bcrypt]

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
