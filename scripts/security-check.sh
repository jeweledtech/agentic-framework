#!/bin/bash
# Security check script - Verify production readiness

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Security & Production Readiness Check${NC}"
echo -e "${GREEN}======================================${NC}"

ISSUES_FOUND=0

# Function to check for pattern
check_pattern() {
    local pattern=$1
    local description=$2
    local severity=$3
    
    echo -n "Checking for $description... "
    
    if grep -r "$pattern" --include="*.py" . 2>/dev/null | grep -v "^#" | grep -v "test" > /dev/null; then
        echo -e "${severity}Found!${NC}"
        echo "  Files with issues:"
        grep -r "$pattern" --include="*.py" . 2>/dev/null | grep -v "^#" | grep -v "test" | head -5
        ((ISSUES_FOUND++))
        return 1
    else
        echo -e "${GREEN}✓ Clean${NC}"
        return 0
    fi
}

# Security Checks
echo -e "\n${YELLOW}1. Development Server Checks${NC}"
echo "================================"

# Check for Flask dev server
check_pattern "app\.run\(" "Flask development server usage" "${RED}✗ CRITICAL: "

# Check for debug mode
check_pattern "debug=True" "Debug mode enabled" "${RED}✗ CRITICAL: "

# Check for development host binding
check_pattern "host=['\"]0\.0\.0\.0['\"].*debug" "Development server on all interfaces" "${YELLOW}⚠ WARNING: "

echo -e "\n${YELLOW}2. Secret Management${NC}"
echo "========================"

# Check for hardcoded secrets
check_pattern "SECRET_KEY\s*=\s*['\"][^'\"\$]" "Hardcoded secret keys" "${RED}✗ CRITICAL: "
check_pattern "API_KEY\s*=\s*['\"][^'\"\$]" "Hardcoded API keys" "${RED}✗ CRITICAL: "
check_pattern "PASSWORD\s*=\s*['\"][^'\"\$]" "Hardcoded passwords" "${RED}✗ CRITICAL: "

echo -e "\n${YELLOW}3. Production Configuration${NC}"
echo "=============================="

# Check for proper server configuration
echo -n "Checking for production server (uvicorn/gunicorn)... "
if grep -r "uvicorn\|gunicorn" --include="*.py" --include="*.sh" --include="Dockerfile" . > /dev/null; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${YELLOW}⚠ Not found - make sure to use production WSGI/ASGI server${NC}"
    ((ISSUES_FOUND++))
fi

# Check for environment variable usage
echo -n "Checking for environment variable usage... "
if grep -r "os\.getenv\|os\.environ" --include="*.py" . > /dev/null; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${YELLOW}⚠ Consider using environment variables for configuration${NC}"
fi

echo -e "\n${YELLOW}4. Docker Security${NC}"
echo "==================="

# Check Dockerfile
if [ -f Dockerfile ]; then
    echo -n "Checking for root user in Dockerfile... "
    if grep -q "USER" Dockerfile; then
        echo -e "${GREEN}✓ Non-root user configured${NC}"
    else
        echo -e "${YELLOW}⚠ Consider running as non-root user${NC}"
        ((ISSUES_FOUND++))
    fi
    
    echo -n "Checking for health checks... "
    if grep -q "HEALTHCHECK" Dockerfile; then
        echo -e "${GREEN}✓ Health check configured${NC}"
    else
        echo -e "${YELLOW}⚠ Consider adding HEALTHCHECK${NC}"
    fi
fi

echo -e "\n${YELLOW}5. API Security${NC}"
echo "================"

# Check for CORS configuration
echo -n "Checking for CORS configuration... "
if grep -r "CORS\|cors" --include="*.py" . > /dev/null; then
    echo -e "${GREEN}✓ CORS configured${NC}"
else
    echo -e "${YELLOW}⚠ No CORS configuration found${NC}"
fi

# Check for rate limiting
echo -n "Checking for rate limiting... "
if grep -r "ratelimit\|limiter\|throttle" --include="*.py" . > /dev/null; then
    echo -e "${GREEN}✓ Rate limiting found${NC}"
else
    echo -e "${YELLOW}⚠ Consider implementing rate limiting${NC}"
fi

echo -e "\n${YELLOW}6. Logging & Monitoring${NC}"
echo "========================"

# Check for logging configuration
echo -n "Checking for logging setup... "
if grep -r "logging\|logger" --include="*.py" . > /dev/null; then
    echo -e "${GREEN}✓ Logging configured${NC}"
else
    echo -e "${YELLOW}⚠ No logging configuration found${NC}"
fi

# Summary
echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}  Summary${NC}"
echo -e "${GREEN}======================================${NC}"

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready for production.${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ISSUES_FOUND issue(s) that should be addressed.${NC}"
    echo
    echo "Recommendations:"
    echo "  1. Never use development servers in production"
    echo "  2. Always disable debug mode"
    echo "  3. Use environment variables for secrets"
    echo "  4. Implement proper logging and monitoring"
    echo "  5. Use production-grade WSGI/ASGI servers (uvicorn/gunicorn)"
    exit 1
fi