# 🏦 SecureBank

A secure banking application built with Django REST, React, and PostgreSQL. Educational project demonstrating enterprise-grade security practices.

---

## ✨ Features

- User authentication with JWT tokens
- Multi-factor authentication (2FA) with OTP
- Secure money transfers with OTP verification
- Bank account & beneficiary management
- Transaction history with audit logging
- Password hashing (PBKDF2 + SHA-256)
- TLS/SSL encryption
- SQL injection & brute-force protection

---
📄 Rapport

👉 [Télécharger le rapport (PDF)](Report_Secure_Bank.pdf)
---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django REST Framework |
| Frontend | React 18+ with Tailwind CSS |
| Database | PostgreSQL |
| Auth | JWT + OTP |

---

## 📦 Installation

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

Access at `http://localhost:3000`

---

## ⚙️ Configuration

### Backend (.env)
```env
DEBUG=False
SECRET_KEY=your-secret-key
DB_NAME=securebank
DB_USER=postgres
DB_PASSWORD=your-password
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api
```

---

## 🚀 Quick Start

1. Register a new account
2. Verify email with OTP
3. Add beneficiary
4. Initiate transfer
5. Confirm with OTP
6. View transaction history

---

## 🔐 Security Features

✅ JWT authentication (15 min tokens)  
✅ OTP verification (6 digits, 5 min validity)  
✅ PBKDF2 password hashing (600k iterations)  
✅ TLS/SSL encryption  
✅ Rate limiting & brute-force protection  
✅ SQL injection prevention (Django ORM)  
✅ CSRF & XSS protection  
✅ Comprehensive audit logging

---

## 📚 API Endpoints

```
POST   /api/auth/register/              # Register user
POST   /api/auth/login/                 # Login
GET    /api/accounts/                   # List accounts
GET    /api/beneficiaries/              # List beneficiaries
POST   /api/beneficiaries/              # Add beneficiary
POST   /api/transfers/initiate/         # Start transfer
POST   /api/transfers/{id}/confirm-otp/ # Confirm with OTP
GET    /api/transactions/               # Transaction history
```

---

## 🧪 Testing

```bash
# Run security tests
python manage.py test security.tests

# Test coverage: SQL Injection, Brute Force, XSS, CSRF, Session Hijacking
```

---

## 📁 Project Structure

```
securebank/
├── backend/          # Django REST API
├── frontend/         # React application
├── docs/             # Documentation
├── Report_Secure_Bank.pdf  # Project report
└── README.md
```

---

## 👥 Authors

- **Ranim Bouraoui** & **Mahmoud Ben Abdelkader**
- Supervised by **Dr. Wafa Berrayana**
- University of Monastir (2025-2026)

---

## ⚠️ Disclaimer

Educational project for demonstrating security best practices. 

