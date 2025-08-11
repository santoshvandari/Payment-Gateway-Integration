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

### Before Going Live:
- [ ] Test eSewa payments with sandbox credentials
- [ ] Test Khalti payments with sandbox credentials
- [ ] Verify webhook endpoints work correctly
- [ ] Test payment success/failure flows
- [ ] Verify email notifications
- [ ] Check database logging
- [ ] Load test the application
- [ ] Security audit

### Payment Gateway Testing:
1. **eSewa Sandbox Testing:**
   - Use test merchant code: EPAYTEST
   - Test various amounts
   - Test success/failure scenarios

2. **Khalti Sandbox Testing:**
   - Use test credentials provided by Khalti
   - Test with test phone numbers
   - Verify webhook responses

## Monitoring and Maintenance

### 1. Logging Setup
```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/payment_gateway.log',
        },
    },
    'loggers': {
        'paymentgateway': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Health Check Endpoint
Add a health check endpoint for monitoring:

```python
# views.py
def health_check(request):
    return JsonResponse({'status': 'healthy', 'timestamp': timezone.now()})
```

### 3. Database Backup
```bash
# Daily backup script
pg_dump payment_gateway_db > backup_$(date +%Y%m%d).sql
```

## Security Best Practices

1. **API Keys Security:**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys regularly
   - Monitor API key usage

2. **Database Security:**
   - Use strong passwords
   - Enable SSL connections
   - Regular security updates
   - Backup encryption

3. **Application Security:**
   - Keep Django updated
   - Use CSRF protection
   - Validate all inputs
   - Implement rate limiting
   - Monitor for suspicious activities

## Troubleshooting

### Common Issues:

1. **Payment Verification Fails:**
   - Check API credentials
   - Verify network connectivity
   - Check webhook URLs
   - Review server logs

2. **Database Connection Issues:**
   - Verify database credentials
   - Check database server status
   - Review connection pool settings

3. **SSL Certificate Issues:**
   - Verify certificate installation
   - Check certificate expiry
   - Test with SSL checker tools

## Support Contacts

- eSewa Support: merchant@esewa.com.np
- Khalti Support: merchant@khalti.com
- Technical Issues: Check logs and contact respective gateway support

## Compliance

Ensure compliance with:
- PCI DSS standards
- Local payment regulations
- Data protection laws
- Financial service regulations
