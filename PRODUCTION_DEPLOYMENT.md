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
