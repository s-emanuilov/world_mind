# GLiNER NER API for Google Cloud Run

Minimal NER API using GLiNER for entity extraction.

## Deployment to Google Cloud Run

```bash
# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Build and deploy (Cloud Run will build from Dockerfile)
gcloud run deploy gliner-ner \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

# Or build with Cloud Build first, then deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gliner-ner
gcloud run deploy gliner-ner \
  --image gcr.io/YOUR_PROJECT_ID/gliner-ner \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

## API Usage

### Health Check
```bash
curl https://YOUR_SERVICE_URL/
```

### Extract Entities
```bash
curl -X POST https://YOUR_SERVICE_URL/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Cristiano Ronaldo plays for Al Nassr.",
    "labels": ["Person", "Teams"],
    "threshold": 0.5
  }'
```

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app:app --reload --port 8080

# Test in another terminal
python test_api.py
```

## Response Format

```json
[
  {
    "text": "Cristiano Ronaldo",
    "label": "Person",
    "start": 0,
    "end": 17,
    "score": 0.95
  }
]
```

