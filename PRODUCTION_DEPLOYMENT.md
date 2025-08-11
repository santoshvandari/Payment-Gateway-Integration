# Production Deployment Guide

## Prerequisites

### 1. eSewa Merchant Account
- Register for eSewa merchant account at: https://merchant.esewa.com.np/
- Complete KYC verification
- Get your merchant code (SCD)
- Test integration in sandbox first

### 2. Khalti Merchant Account
- Register at: https://khalti.com/join/merchant/
- Complete verification process
- Get live API keys (public and secret)
- Test with sandbox keys first

## Deployment Steps

### 1. Environment Setup
```bash
# Copy production environment template
cp .env.production .env

# Update with your actual credentials
nano .env
```

### 2. Database Setup (Production)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb payment_gateway_db
sudo -u postgres createuser payment_user

# Update .env with database URL
DATABASE_URL=postgres://payment_user:password@localhost/payment_gateway_db
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install psycopg2-binary  # for PostgreSQL
pip install gunicorn  # for production server
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Security Checklist
- [ ] Update SECRET_KEY with strong random key
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS (SSL certificate)
- [ ] Set up proper database (PostgreSQL/MySQL)
- [ ] Configure email backend
- [ ] Set up monitoring and logging
- [ ] Regular database backups

### 7. Server Configuration (Nginx + Gunicorn)

#### Gunicorn Configuration
```bash
# Create gunicorn config
nano /etc/systemd/system/payment-gateway.service
```

```ini
[Unit]
Description=Payment Gateway Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Payment-Gateway-Integration
ExecStart=/path/to/venv/bin/gunicorn core.wsgi:application --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/Payment-Gateway-Integration/staticfiles/;
    }
}
```

### 8. SSL Certificate (Let's Encrypt)
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Testing Checklist

### Payment Gateway Testing:
1. **eSewa Sandbox Testing:**
   - Use test merchant code: EPAYTEST
   - Test various amounts
   - Test success/failure scenarios

2. **Khalti Sandbox Testing:**
   - Use test credentials provided by Khalti
   - Test with test phone numbers
   - Verify webhook responses

