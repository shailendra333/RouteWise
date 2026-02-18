# Deployment Guide - Smart Logistics System

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Configuration](#configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS 10.15+, or Windows 10+
- **Node.js**: Version 18.0 or higher
- **Python**: Version 3.8 or higher
- **Git**: Latest version
- **Docker**: Version 20.10+ (for containerized deployment)

### Required Software
```bash
# Node.js and npm
node --version  # Should be 18.0+
npm --version   # Should be 8.0+

# Python and pip
python3 --version  # Should be 3.8+
pip3 --version     # Should be 21.0+

# Git
git --version

# Docker (optional)
docker --version
docker-compose --version
```

## 🏠 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/smart-logistics-system.git
cd smart-logistics-system
```

### 2. Frontend Setup
```bash
# Install frontend dependencies
npm install

# Start development server
npm run dev
```
The frontend will be available at `http://localhost:5173`

### 3. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python app.py
```
The backend will be available at `http://localhost:5000`

### 4. Environment Configuration
Create a `.env` file in the root directory:
```bash
# Frontend environment variables
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=Smart Logistics System

# Backend environment variables
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///smart_logistics.db
CORS_ORIGINS=http://localhost:5173
```

### 5. Verify Installation
1. Open `http://localhost:5173` in your browser
2. Log in with demo credentials: demo@smartlogistics.com / demo123
3. Test basic functionality (dashboard, data upload, route optimization)

## 🚀 Production Deployment

### 1. Build Frontend
```bash
# Build optimized production bundle
npm run build

# The build files will be in the 'dist' directory
ls dist/
```

### 2. Configure Production Environment
Create production environment file:
```bash
# .env.production
VITE_API_URL=https://your-api-domain.com
VITE_APP_NAME=Smart Logistics System

# Backend production settings
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
CORS_ORIGINS=https://your-frontend-domain.com
```

### 3. Database Setup (PostgreSQL)
```sql
-- Create database
CREATE DATABASE smart_logistics;

-- Create user
CREATE USER logistics_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE smart_logistics TO logistics_user;
```

### 4. Backend Production Setup
```bash
# Install production dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Run database migrations
python app.py

# Start production server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 5. Web Server Configuration (Nginx)
```nginx
# /etc/nginx/sites-available/smart-logistics
server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    location / {
        root /path/to/smart-logistics/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/smart-logistics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🐳 Docker Deployment

### 1. Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Individual Container Deployment

#### Backend Container
```bash
# Build backend image
cd backend
docker build -t smart-logistics-backend .

# Run backend container
docker run -d \
  --name logistics-backend \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  smart-logistics-backend
```

#### Frontend Container
```bash
# Build frontend image
docker build -f Dockerfile.frontend -t smart-logistics-frontend .

# Run frontend container
docker run -d \
  --name logistics-frontend \
  -p 3000:3000 \
  smart-logistics-frontend
```

### 3. Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - backend_data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://backend:5000
    restart: unless-stopped

  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=smart_logistics
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  backend_data:
  postgres_data:
```

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance Setup
```bash
# Launch EC2 instance (Ubuntu 20.04 LTS)
# Security groups: HTTP (80), HTTPS (443), SSH (22)

# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker ubuntu
```

#### 2. Deploy Application
```bash
# Clone repository
git clone https://github.com/yourusername/smart-logistics-system.git
cd smart-logistics-system

# Set environment variables
cp .env.example .env
# Edit .env with production values

# Deploy with Docker Compose
docker-compose up -d
```

#### 3. RDS Database Setup
```bash
# Create RDS PostgreSQL instance
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/smart_logistics
```

### Google Cloud Platform

#### 1. Cloud Run Deployment
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/smart-logistics-backend backend/
gcloud builds submit --tag gcr.io/PROJECT_ID/smart-logistics-frontend .

# Deploy to Cloud Run
gcloud run deploy smart-logistics-backend \
  --image gcr.io/PROJECT_ID/smart-logistics-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy smart-logistics-frontend \
  --image gcr.io/PROJECT_ID/smart-logistics-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### 1. Container Instances
```bash
# Create resource group
az group create --name smart-logistics --location eastus

# Deploy backend
az container create \
  --resource-group smart-logistics \
  --name logistics-backend \
  --image your-registry/smart-logistics-backend \
  --ports 5000 \
  --environment-variables FLASK_ENV=production

# Deploy frontend
az container create \
  --resource-group smart-logistics \
  --name logistics-frontend \
  --image your-registry/smart-logistics-frontend \
  --ports 3000
```

## ⚙️ Configuration

### Environment Variables

#### Frontend (.env)
```bash
# API Configuration
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=Smart Logistics System
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_EXPORT=true
VITE_DEBUG_MODE=false
```

#### Backend (.env)
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:port/db
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=30

# CORS Configuration
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# ML Model Configuration
MODEL_CACHE_SIZE=100
TRAINING_BATCH_SIZE=32
PREDICTION_CACHE_TTL=3600

# File Upload Configuration
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=csv,xlsx,json

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/smart-logistics.log
```

### Database Configuration

#### PostgreSQL Production Setup
```sql
-- Performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Restart PostgreSQL
SELECT pg_reload_conf();
```

#### Database Indexes
```sql
-- Create performance indexes
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_routes_date ON optimized_routes(optimization_date);
CREATE INDEX idx_forecasts_date ON demand_forecasts(forecast_date);
```

### Security Configuration

#### SSL/TLS Setup
```nginx
# Nginx SSL configuration
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
}
```

## 📊 Monitoring & Maintenance

### Health Checks

#### Application Health Endpoint
```python
# Backend health check
@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'database': check_database_connection(),
        'memory_usage': get_memory_usage()
    }
```

#### Monitoring Script
```bash
#!/bin/bash
# health_check.sh

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "Frontend: OK"
else
    echo "Frontend: FAILED"
fi

# Check backend
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
fi

# Check database
if docker exec postgres pg_isready > /dev/null 2>&1; then
    echo "Database: OK"
else
    echo "Database: FAILED"
fi
```

### Logging Configuration

#### Application Logging
```python
# Python logging configuration
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/smart_logistics.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

#### Log Rotation
```bash
# /etc/logrotate.d/smart-logistics
/var/log/smart-logistics/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx
    endscript
}
```

### Backup Strategy

#### Database Backup
```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="smart_logistics"

# Create backup
pg_dump $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

#### Application Data Backup
```bash
#!/bin/bash
# backup_application.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
APP_DIR="/path/to/smart-logistics"

# Create application backup
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    --exclude=node_modules \
    --exclude=venv \
    --exclude=.git \
    $APP_DIR

echo "Application backup completed: app_backup_$DATE.tar.gz"
```

### Performance Monitoring

#### System Metrics Script
```bash
#!/bin/bash
# monitor_performance.sh

echo "=== System Performance Report ==="
echo "Date: $(date)"
echo

echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2 $3 $4 $5}'

echo "Memory Usage:"
free -h

echo "Disk Usage:"
df -h

echo "Docker Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "Application Response Times:"
curl -w "Frontend: %{time_total}s\n" -o /dev/null -s http://localhost:3000
curl -w "Backend: %{time_total}s\n" -o /dev/null -s http://localhost:5000/api/health
```

### Automated Maintenance

#### Cron Jobs
```bash
# Add to crontab (crontab -e)

# Daily database backup at 2 AM
0 2 * * * /path/to/backup_database.sh

# Weekly application backup on Sundays at 3 AM
0 3 * * 0 /path/to/backup_application.sh

# Daily log cleanup at 1 AM
0 1 * * * find /var/log/smart-logistics -name "*.log" -mtime +7 -delete

# Hourly health check
0 * * * * /path/to/health_check.sh >> /var/log/health_check.log

# Daily performance report at 6 AM
0 6 * * * /path/to/monitor_performance.sh >> /var/log/performance.log
```

### Troubleshooting

#### Common Issues

**Issue**: Application won't start
```bash
# Check logs
docker-compose logs -f

# Check port conflicts
netstat -tulpn | grep :5000
netstat -tulpn | grep :3000

# Restart services
docker-compose restart
```

**Issue**: Database connection errors
```bash
# Check database status
docker exec postgres pg_isready

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

**Issue**: High memory usage
```bash
# Check memory usage
docker stats

# Restart containers
docker-compose restart

# Check for memory leaks
docker exec backend ps aux --sort=-%mem
```

---

*This deployment guide provides comprehensive instructions for setting up the Smart Logistics System in various environments. Follow the appropriate section based on your deployment needs.*