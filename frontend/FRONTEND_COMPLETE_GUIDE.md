# 🏦 Secure Banking Frontend - Guide Complet

## Table des Matières
1. [Structure du Projet](#structure-du-projet)
2. [Installation & Configuration](#installation--configuration)
3. [Guide de Développement](#guide-de-développement)
4. [Intégration avec Django](#intégration-avec-django)
5. [Mesures de Sécurité](#mesures-de-sécurité)
6. [Tests](#tests)
7. [Déploiement](#déploiement)

---

## Structure du Projet

\`\`\`
secure-banking-frontend/
│
├── app/
│   ├── layout.tsx                 # Layout principal avec metadata
│   ├── page.tsx                   # Page d'accueil / Application complète
│   └── globals.css                # Styles globaux
│
├── components/
│   ├── ui/                        # Composants shadcn/ui réutilisables
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   └── ... (autres UI components)
│   │
│   ├── auth/
│   │   ├── LoginForm.tsx          # Formulaire de connexion
│   │   └── RegisterForm.tsx       # Formulaire d'inscription
│   │
│   ├── transfers/
│   │   ├── TransferForm.tsx       # Formulaire de virement
│   │   ├── TransferConfirmation.tsx
│   │   └── OTPVerification.tsx
│   │
│   ├── beneficiaries/
│   │   ├── BeneficiaryList.tsx
│   │   ├── AddBeneficiary.tsx
│   │   └── EditBeneficiary.tsx
│   │
│   ├── accounts/
│   │   ├── AccountsList.tsx
│   │   └── AccountCard.tsx
│   │
│   ├── transactions/
│   │   ├── TransactionHistory.tsx
│   │   └── TransactionFilter.tsx
│   │
│   ├── profile/
│   │   ├── ProfileSettings.tsx
│   │   ├── ChangePassword.tsx
│   │   └── PersonalInfo.tsx
│   │
│   ├── common/
│   │   ├── Navbar.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorAlert.tsx
│   │
│   └── theme-provider.tsx         # Thème et context providers
│
├── hooks/
│   ├── useAuth.ts                 # Gestion authentification
│   ├── useAccounts.ts             # Gestion des comptes
│   ├── useBeneficiaries.ts        # Gestion des bénéficiaires
│   ├── useTransactions.ts         # Gestion des transactions
│   ├── useProfile.ts              # Gestion du profil
│   └── use-mobile.ts              # Responsive design
│
├── lib/
│   ├── api/
│   │   ├── api.ts                 # Configuration Axios
│   │   ├── auth.ts                # Endpoints authentification
│   │   ├── accounts.ts            # Endpoints comptes
│   │   ├── beneficiaries.ts       # Endpoints bénéficiaires
│   │   ├── transactions.ts        # Endpoints transactions
│   │   ├── profile.ts             # Endpoints profil
│   │   ├── otp.ts                 # Endpoints OTP
│   │   ├── audit.ts               # Endpoints audit
│   │   └── index.ts               # Exports centralisés
│   │
│   ├── utils/
│   │   ├── validators.ts          # Validateurs Zod
│   │   └── format.ts              # Formatage des données
│   │
│   ├── constants/
│   │   └── index.ts               # Constantes globales
│   │
│   └── utils.ts                   # Utilitaires généraux
│
├── public/                        # Assets statiques
│   └── images/
│
├── styles/                        # Styles CSS additionnels
│   └── globals.css
│
├── .env.local                     # Variables d'environnement (local)
├── .env.example                   # Exemple variables d'environnement
├── .gitignore
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.mjs
├── components.json
└── README.md
\`\`\`

---

## Installation & Configuration

### 1. Installation des Dépendances

\`\`\`bash
# Installation
npm install

# Ou avec yarn
yarn install
\`\`\`

### 2. Configuration des Variables d'Environnement

Créer un fichier `.env.local`:

\`\`\`env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# App Configuration
NEXT_PUBLIC_APP_NAME=Secure Banking
NEXT_PUBLIC_APP_VERSION=1.0.0

# Security
NEXT_PUBLIC_OTP_TIMEOUT=300
NEXT_PUBLIC_SESSION_TIMEOUT=1800
\`\`\`

### 3. Lancer le Serveur de Développement

\`\`\`bash
npm run dev
\`\`\`

L'application sera accessible à `http://localhost:3000`

---

## Guide de Développement

### Architecture Globale

\`\`\`
User Interface (Components)
    ↓
State Management (Hooks)
    ↓
API Services (lib/api)
    ↓
HTTP Client (Axios with Interceptors)
    ↓
Django Backend
\`\`\`

### Flux de Données

#### Exemple: Effectuer un Virement

1. **Utilisateur remplit le formulaire** → TransferForm.tsx
2. **Form validation** → Zod schemas dans lib/utils/validators.ts
3. **Appel du hook** → useTransactions.ts
4. **Hook appelle l'API** → lib/api/transactions.ts
5. **API effectue la requête** → axios avec JWT interceptor
6. **Response reçue** → Hook met à jour le state
7. **Component re-render** → UI mise à jour avec confirmation

### Patterns Importants

#### Pattern 1: Hooks personnalisés

\`\`\`typescript
// hooks/useAuth.ts
import { useState } from 'react';
import { authAPI } from '@/lib/api';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authAPI.login(email, password);
      setUser(response.data.user);
      localStorage.setItem('token', response.data.token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { user, loading, error, login };
}
\`\`\`

#### Pattern 2: Validation Zod

\`\`\`typescript
// lib/utils/validators.ts
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(8, 'Mot de passe trop court'),
});

export type LoginInput = z.infer<typeof loginSchema>;
\`\`\`

#### Pattern 3: Composants avec React Hook Form

\`\`\`typescript
// components/auth/LoginForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema } from '@/lib/utils/validators';

export function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    // Appeler l'API
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Formulaire */}
    </form>
  );
}
\`\`\`

---

## Intégration avec Django

### Configuration du Backend Django

**settings.py:**

\`\`\`python
# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

CORS_ALLOW_CREDENTIALS = True

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
\`\`\`

### Configuration Axios (Frontend)

**lib/api/api.ts:**

\`\`\`typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor pour ajouter le token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = \`Bearer \${token}\`;
  }
  return config;
});

// Interceptor pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expiré, rediriger vers login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
\`\`\`

---

## Mesures de Sécurité

### 1. Authentification & Tokens JWT

- ✅ Tokens stockés en localStorage avec expiration
- ✅ Refresh tokens automatiques
- ✅ Auto-logout en cas de token expiré
- ✅ CORS configuré correctement

### 2. Validation des Entrées

- ✅ Validation côté client avec Zod
- ✅ Validation côté serveur obligatoire
- ✅ Sanitization des inputs
- ✅ Masquage des données sensibles

### 3. Protection XSS

- ✅ Échappement automatique avec React
- ✅ Content Security Policy headers
- ✅ Pas d'innerHTML dangereux

### 4. Protection CSRF

- ✅ CORS bien configuré
- ✅ SameSite cookies
- ✅ Tokens CSRF sur requêtes sensibles

### 5. Communication Sécurisée

- ✅ HTTPS en production
- ✅ Cookies HttpOnly
- ✅ Headers de sécurité

### 6. Gestion des Erreurs

- ✅ Messages d'erreur génériques pour l'utilisateur
- ✅ Logs détaillés côté serveur
- ✅ Pas d'exposition des stacks traces

---

## Tests

### Tests Unitaires

\`\`\`bash
# Installation Jest
npm install --save-dev jest @testing-library/react

# Exécuter les tests
npm test
\`\`\`

### Tests d'Intégration

\`\`\`bash
# Installation Playwright
npm install --save-dev @playwright/test

# Exécuter les tests E2E
npm run test:e2e
\`\`\`

### Exemple Test: Formulaire de Connexion

\`\`\`typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from '@/components/auth/LoginForm';

describe('LoginForm', () => {
  it('should submit form with valid credentials', async () => {
    render(<LoginForm />);
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    await screen.findByText(/Success/i);
  });
});
\`\`\`

---

## Déploiement

### Build pour Production

\`\`\`bash
npm run build
npm start
\`\`\`

### Déploiement sur Vercel

\`\`\`bash
# Installation Vercel CLI
npm i -g vercel

# Déployer
vercel
\`\`\`

### Variables d'Environnement en Production

Ajouter dans Vercel Dashboard → Settings → Environment Variables:

- `NEXT_PUBLIC_API_URL=https://api.banking.tn/api`
- `NEXT_PUBLIC_OTP_TIMEOUT=300`

### Checklist Avant Production

- [ ] `DEBUG = false` dans Django
- [ ] HTTPS activé
- [ ] CORS correctement configuré
- [ ] JWT secrets forts
- [ ] Email bien configuré
- [ ] Database backups automatiques
- [ ] Monitoring activé
- [ ] Rate limiting en place
- [ ] WAF configuré
- [ ] Logs rotatifs

---

## Support & Ressources

- **Documentation Next.js**: https://nextjs.org/docs
- **Documentation Django**: https://docs.djangoproject.com
- **Zod Validation**: https://zod.dev
- **shadcn/ui**: https://ui.shadcn.com

---

**Dernière mise à jour**: Janvier 2025
**Version**: 1.0.0
