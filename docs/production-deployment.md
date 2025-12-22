# Production Deployment Guide

## ⚠️ CRITICAL SECURITY WARNING

**NEVER use development servers in production!** This includes:
- Flask's built-in server (`app.run()`)
- Django's runserver
- Any server that displays "WARNING: This is a development server"

## Why This Matters

Development servers are:
- **Single-threaded**: Can only handle one request at a time
- **Not secure**: May expose debugging information
- **Unstable**: Not designed for continuous operation
- **No process management**: Won't restart on failure

## Production Server Configuration

### Using Uvicorn (Recommended for FastAPI)

The Agentic Framework uses **uvicorn**, a production-ready ASGI server.

#### Basic Production Setup
```python
# api_server.py - Current implementation (Good for production)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Enhanced Production Configuration
```python
# For better performance with multiple workers
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Multiple worker processes
        loop="uvloop",  # Faster event loop
        log_level="info"
    )
```

### Alternative: Using Gunicorn with Uvicorn Workers

For even better production performance:

```bash
# Install gunicorn
pip install gunicorn

# Run with uvicorn workers
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Docker Production Configuration

Update your `Dockerfile` for production:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Security: Don't run as root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Use gunicorn for production
CMD ["gunicorn", "api_server:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

## Security Checklist

### Pre-Deployment
- [ ] No development servers in use
- [ ] All debug modes disabled
- [ ] Environment variables properly set
- [ ] Secrets not hardcoded
- [ ] SSL/TLS configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured

### Verification Commands

```bash
# Check server headers (should NOT show Werkzeug or development server)
curl -I https://your-api.com | grep Server

# Expected output:
# Server: uvicorn
# or
# Server: gunicorn/20.1.0
```

## Environment Variables

Create a `.env.production` file:

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com

# API Configuration
API_WORKERS=4
API_TIMEOUT=120

# Ollama Configuration
OLLAMA_HOST=ollama:11434
MODEL_PATH=llama3.2:3b
```

## Monitoring and Health Checks

### Health Check Endpoint

The framework includes a `/health` endpoint. Use it for:
- Load balancer health checks
- Kubernetes liveness/readiness probes
- Monitoring systems

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Prometheus Metrics (Optional)

Add metrics collection:

```python
from prometheus_client import Counter, Histogram, generate_latest

# Add metrics
request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'API request duration')

@app.middleware("http")
async def add_metrics(request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Scaling Considerations

### Horizontal Scaling

1. **Use a load balancer** (nginx, HAProxy, or cloud load balancer)
2. **Run multiple instances** of the API server
3. **Use Redis** for shared state/caching
4. **Implement database connection pooling**

### Example Nginx Configuration

```nginx
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 443 ssl http2;
    server_name api.your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Common Pitfalls to Avoid

1. **Never expose debug mode in production**
   ```python
   # WRONG
   app = FastAPI(debug=True)  # Never in production!
   
   # RIGHT
   app = FastAPI(debug=False)
   ```

2. **Don't hardcode secrets**
   ```python
   # WRONG
   SECRET_KEY = "my-secret-key"
   
   # RIGHT
   SECRET_KEY = os.getenv("SECRET_KEY")
   ```

3. **Always use HTTPS in production**
   - Use Let's Encrypt for free SSL certificates
   - Redirect all HTTP to HTTPS

4. **Implement rate limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=lambda: request.client.host)
   app.state.limiter = limiter
   ```

## Deployment Script Example

Create a `deploy-production.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying to production..."

# Build Docker image
docker build -t agentic-framework:latest .

# Run security checks
echo "🔒 Running security checks..."
docker run --rm agentic-framework:latest python -c "
import sys
# Check for development server patterns
with open('api_server.py', 'r') as f:
    content = f.read()
    if 'debug=True' in content:
        print('ERROR: Debug mode detected!')
        sys.exit(1)
print('✅ Security checks passed')
"

# Deploy with Docker Compose
docker-compose -f docker-compose.production.yml up -d

echo "✅ Deployment complete!"
```

## Support and Resources

- [FastAPI Production Deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Remember: Production deployment is about security, stability, and scalability. Never compromise on these principles.**