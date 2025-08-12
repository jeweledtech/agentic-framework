#!/bin/bash
# Production deployment script for JeweledTech Agentic Framework
# Ensures safe deployment with production-ready servers

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  JeweledTech Agentic Framework${NC}"
echo -e "${GREEN}  Production Deployment Script${NC}"
echo -e "${GREEN}======================================${NC}"

# Step 1: Security checks
echo -e "\n${YELLOW}Running security checks...${NC}"

# Check for development server patterns
echo "Checking for unsafe development server usage..."
if grep -r "debug=True" --include="*.py" . 2>/dev/null | grep -v "^#"; then
    echo -e "${RED}✗ Found debug=True in Python files!${NC}"
    echo "Please set debug=False for production"
    exit 1
fi

if grep -r "app\.run.*host.*0\.0\.0\.0" --include="*.py" . 2>/dev/null | grep -v "^#"; then
    echo -e "${YELLOW}⚠ Found app.run with 0.0.0.0 binding${NC}"
    echo "Note: Using uvicorn for production deployment instead"
fi

echo -e "${GREEN}✓ Security checks passed${NC}"

# Step 2: Environment setup
echo -e "\n${YELLOW}Setting up environment...${NC}"

# Check for .env.production
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}Creating .env.production from template...${NC}"
    cat > .env.production <<EOF
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Ollama Configuration
OLLAMA_HOST=ollama:11434
MODEL_PATH=llama3.2:3b

# Security (generate your own keys!)
SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo -e "${GREEN}✓ Created .env.production${NC}"
    echo -e "${YELLOW}  Please review and update with your values${NC}"
fi

# Step 3: Build Docker image
echo -e "\n${YELLOW}Building Docker image...${NC}"
docker build -t agentic-framework:production .

# Step 4: Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
docker run --rm agentic-framework:production python -c "
import sys
sys.path.append('/app')
from api_server import app
print('✓ API server imports successfully')
from agents.executive_chat import ExecutiveChatAgent
print('✓ Executive chat agent imports successfully')
"

# Step 5: Create production docker-compose
echo -e "\n${YELLOW}Creating production Docker Compose configuration...${NC}"
cat > docker-compose.production.yml <<'EOF'
version: '3.8'

services:
  api:
    image: agentic-framework:production
    container_name: agentic-framework-api-prod
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./knowledge_bases:/app/knowledge_bases:ro
      - ./logs:/app/logs
    depends_on:
      - ollama
    networks:
      - agentic-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
        reservations:
          memory: 1G
          cpus: '1'

  ollama:
    image: ollama/ollama:latest
    container_name: agentic-framework-ollama-prod
    restart: always
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - agentic-network
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: agentic-framework-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - agentic-network

volumes:
  ollama-data:
    driver: local

networks:
  agentic-network:
    driver: bridge
EOF

echo -e "${GREEN}✓ Created docker-compose.production.yml${NC}"

# Step 6: Deploy
echo -e "\n${YELLOW}Starting production deployment...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Step 7: Verify deployment
echo -e "\n${YELLOW}Verifying deployment...${NC}"
sleep 10

# Check health endpoint
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API server is healthy${NC}"
    
    # Check server type
    SERVER_HEADER=$(curl -I http://localhost:8000 2>/dev/null | grep -i "server:" || true)
    if echo "$SERVER_HEADER" | grep -i "werkzeug" > /dev/null; then
        echo -e "${RED}✗ WARNING: Development server detected!${NC}"
        echo "Please ensure you're using uvicorn or gunicorn"
    else
        echo -e "${GREEN}✓ Production server verified${NC}"
    fi
else
    echo -e "${RED}✗ API server health check failed${NC}"
    echo "Check logs: docker-compose -f docker-compose.production.yml logs api"
    exit 1
fi

# Step 8: Display status
echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo
echo "Services running:"
echo "  • API Server: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Ollama: http://localhost:11434"
echo
echo "Next steps:"
echo "  1. Configure nginx for SSL (if using)"
echo "  2. Set up monitoring"
echo "  3. Configure backups"
echo "  4. Test executive chat: curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"message\":\"Hello\"}"
echo
echo "Useful commands:"
echo "  • View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  • Stop services: docker-compose -f docker-compose.production.yml down"
echo "  • Restart: docker-compose -f docker-compose.production.yml restart"