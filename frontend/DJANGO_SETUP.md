# Configuration Django pour le Frontend

## 1. Installation des dépendances

\`\`\`bash
pip install django-cors-headers djangorestframework python-decouple
\`\`\`

## 2. Configuration CORS (settings.py)

\`\`\`python
# settings.py
INSTALLED_APPS = [
    # ... vos apps
    'corsheaders',
    'rest_framework',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Ajouter avant CommonMiddlewareMiddleware
    'django.middleware.common.CommonMiddlewareMiddleware',
    # ... rest of middleware
]

# Configuration CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Development
    "http://127.0.0.1:3000",      # Development
    "https://yourdomain.com",     # Production
]

CORS_ALLOW_CREDENTIALS = True  # Pour les cookies HttpOnly

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
\`\`\`

## 3. Configuration Rest Framework (settings.py)

\`\`\`python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
\`\`\`

## 4. Structure des URLs Django (urls.py)

\`\`\`python
# urls.py principal
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls.auth')),
    path('api/accounts/', include('accounts.urls.accounts')),
    path('api/profile/', include('accounts.urls.profile')),
    path('api/beneficiaries/', include('accounts.urls.beneficiaries')),
    path('api/transactions/', include('transactions.urls')),
    path('api/otp/', include('accounts.urls.otp')),
]
\`\`\`

## 5. Response Format Standard

Toutes les réponses API doivent suivre ce format:

### Succès (200, 201)
\`\`\`json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
\`\`\`

### Erreur (400, 401, 404, 500)
\`\`\`json
{
  "success": false,
  "error": "Description of the error",
  "status": 400
}
\`\`\`

## 6. Authentification JWT

### Login Response
\`\`\`json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "userId": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
\`\`\`

### Using Token in Headers
\`\`\`
Authorization: Bearer {token}
\`\`\`

## 7. Rate Limiting (Optional)

\`\`\`python
# settings.py
REST_FRAMEWORK = {
    # ... existing config
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
\`\`\`

## 8. Audit & Logging

\`\`\`python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/banking.log',
        },
    },
    'loggers': {
        'transactions': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
\`\`\`

## 9. Verification Checklist

- [ ] CORS headers configurés correctement
- [ ] JWT authentication implémentée
- [ ] OTP sending/verification en place
- [ ] Email templates créées pour confirmations
- [ ] ACID transactions implémentées pour les transferts
- [ ] Rate limiting activé
- [ ] Logging & audit trail configuré
- [ ] HTTPS en production
