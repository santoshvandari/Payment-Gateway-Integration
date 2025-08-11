# Payment Gateway Integration - Django

A production-ready Django application demonstrating comprehensive payment gateway integration with **eSewa** and **Khalti** - Nepal's leading digital payment platforms.

![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)


## Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Django** | Web Framework | 5.2.5 |
| **Python** | Backend Language | 3.8+ |
| **SQLite/PostgreSQL** | Database | Latest |
| **Bootstrap** | Frontend Framework | 5.3 |
| **JavaScript** | Frontend Logic | ES6+ |
| **Font Awesome** | Icons | 6.0+ |
| **AOS** | Animations | 2.3+ |

## Prerequisites

- Python 3.8 or higher
- Django 5.2.5
- Git
- Virtual Environment (recommended)

### For Production:
- PostgreSQL or MySQL
- Nginx (recommended)
- SSL Certificate
- eSewa Merchant Account
- Khalti Merchant Account

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/santoshvandari/Payment-Gateway-Integration.git
cd Payment-Gateway-Integration
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Update with your credentials (for production)
nano .env
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the application.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost

# Payment Gateway Mode
PAYMENT_GATEWAY_MODE=sandbox  # or 'production'

# eSewa Configuration
ESEWA_SCD=EPAYTEST  # Your merchant code
ESEWA_SUCCESS_URL=http://127.0.0.1:8000/payment/esewa-success/
ESEWA_FAILURE_URL=http://127.0.0.1:8000/payment/esewa-failure/
ESEWA_PAYMENT_URL=https://epay.esewa.com.np/api/epay/main/v2/form

# Khalti Configuration
KHALTI_PUBLIC_KEY=test_public_key_your_key_here
KHALTI_SECRET_KEY=test_secret_key_your_key_here
KHALTI_SUCCESS_URL=http://127.0.0.1:8000/payment/khalti-success/
KHALTI_FAILURE_URL=http://127.0.0.1:8000/payment/khalti-failure/
KHALTI_WEBSITE_URL=http://127.0.0.1:8000/
```

## Usage

### Creating Orders
1. Navigate to `/payment/create-test-order/`
2. Fill in customer details and amount
3. Submit to create a new order

### Payment Process
1. Go to order checkout page
2. Select payment method (eSewa or Khalti)
3. Complete payment through gateway
4. View order success page

### Admin Panel
- Access at `/admin/`
- View orders, payment logs, and analytics
- Monitor transaction status and details

## Project Structure

```
Payment-Gateway-Integration/
├── core/                          # Django project settings
│   ├── settings.py               # Main configuration
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI application
├── paymentgateway/               # Main application
│   ├── models.py                 # Database models
│   ├── views.py                  # Business logic
│   ├── urls.py                   # App URL patterns
│   ├── admin.py                  # Admin interface
│   └── payment_gateways.py       # Payment gateway logic
├── Templates/                    # HTML templates
│   ├── base.html                 # Base template
│   ├── order_checkout.html       # Checkout page
│   ├── order_success.html        # Success page
│   ├── payment_form.html         # Payment form
│   └── esewa_demo.html          # Demo page
├── static/                       # Static files
│   ├── css/                      # Stylesheets
│   ├── js/                       # JavaScript files
│   └── images/                   # Images
├── requirements.txt              # Python dependencies
├── .env.production              # Production environment template
├── PRODUCTION_DEPLOYMENT.md     # Deployment guide
└── README.md                    # This file
```

## Payment Gateway Integration

### eSewa Integration

**Sandbox Testing:**
- Merchant Code: `EPAYTEST`
- Test URL: Sandbox environment
- No real money transactions

**Production:**
- Get merchant account from [eSewa](https://merchant.esewa.com.np/)
- Update credentials in `.env`
- Switch to production mode

### Khalti Integration

**Sandbox Testing:**
- Use test API keys provided
- Test phone numbers available
- Sandbox environment

**Production:**
- Register at [Khalti Merchant](https://khalti.com/join/merchant/)
- Complete KYC verification
- Get live API credentials

## Testing

### Sandbox Testing
```bash
# Set environment to sandbox
PAYMENT_GATEWAY_MODE=sandbox

# Run tests
python manage.py test
```

## Production Deployment

For production deployment, follow the detailed guide in [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md).

### Quick Production Setup
1. Get merchant accounts (eSewa & Khalti)
2. Update `.env` with live credentials
3. Set `PAYMENT_GATEWAY_MODE=production`
4. Deploy with proper web server (Nginx + Gunicorn)
5. Enable HTTPS
6. Monitor transactions

## Database Schema

### Order Model
```python
- order_id: Unique identifier
- name: Customer name
- email: Customer email
- phone: Customer phone
- total_price: Order amount
- is_paid: Payment status
- payment_method: Gateway used
- transaction_id: Gateway transaction ID
- status: Order status
- created_at: Creation timestamp
```

### PaymentLog Model
```python
- order: Foreign key to Order
- payment_method: Gateway name
- transaction_id: Gateway transaction ID
- amount: Transaction amount
- status: Transaction status
- gateway_response: Raw gateway response
- ip_address: Customer IP
- user_agent: Browser information
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
