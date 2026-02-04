# multiply Microservice

Extracted service from canonical code analysis.

## Running

### Local Development
```
pip install -r requirements.txt
python api.py
```

### Docker
```
docker build -t multiply .
docker run -p 8000:8000 multiply
```

### Kubernetes
```
kubectl apply -f deployment.yaml
```

## API Endpoints

- POST /execute - Execute service logic
- GET /health - Health check

## Directives
extract
