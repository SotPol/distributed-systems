FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install quart aiohttp
CMD ["python", "master.py"]
