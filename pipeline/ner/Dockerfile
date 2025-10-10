FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Download model at build time to speed up cold starts
RUN python -c "from gliner import GLiNER; GLiNER.from_pretrained('urchade/gliner_medium-v2.1')"

# Cloud Run expects the container to listen on PORT env variable
ENV PORT=8080

# Run the application
CMD uvicorn app:app --host 0.0.0.0 --port $PORT

