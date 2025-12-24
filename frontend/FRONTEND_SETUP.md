# Configuration Frontend Next.js

## 1. Installation des dépendances

\`\`\`bash
npm install axios
\`\`\`

## 2. Variables d'environnement (.env.local)

\`\`\`env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
\`\`\`

## 3. Structure des fichiers

\`\`\`
src/
├── app/
│   └── page.tsx              # Main app component
├── lib/
│   ├── api/
│   │   ├── api.ts            # Axios configuration + interceptors
│   │   ├── auth.ts           # Authentication endpoints
│   │   ├── accounts.ts       # Accounts endpoints
│   │   ├── beneficiaries.ts  # Beneficiaries endpoints
│   │   ├── transactions.ts   # Transactions endpoints
│   │   └── index.ts          # Export all APIs
│   └── constants.ts          # Validation rules & constants
├── hooks/
│   ├── useAuth.ts            # Authentication hook
│   ├── useAccounts.ts        # Accounts hook
│   ├── useBeneficiaries.ts   # Beneficiaries hook
│   └── useTransactions.ts    # Transactions hook
└── components/
    ├── LoadingSpinner.tsx    # Loading component
    ├── ErrorAlert.tsx        # Error display
    └── SuccessAlert.tsx      # Success message
\`\`\`

## 4. Utilisation des Hooks dans les Composants

\`\`\`typescript
import { useAuth } from '@/hooks/useAuth'
import { useAccounts } from '@/hooks/useAccounts'
import { useTransactions } from '@/hooks/useTransactions'

export default function Dashboard() {
  const { user, loading: authLoading } = useAuth()
  const { accounts, loading: accountsLoading } = useAccounts()
  const { transactions, initiateTransaction } = useTransactions()

  if (authLoading || accountsLoading) return <LoadingSpinner />

  return (
    <div>
      {/* Component JSX */}
    </div>
  )
}
\`\`\`

## 5. Gestion des erreurs API

\`\`\`typescript
import { handleAPIError } from '@/lib/api'

try {
  const response = await authAPI.login({ email, password })
  // Handle success
} catch (error) {
  const { error: message, status } = handleAPIError(error)
  console.error(`Error [${status}]: ${message}`)
}
\`\`\`

## 6. Appels API directs

\`\`\`typescript
import { transactionsAPI } from '@/lib/api'

// Initier une transaction
const response = await transactionsAPI.initiateTransaction({
  fromAccountId: 'account-uuid',
  toBeneficiaryId: 'beneficiary-uuid',
  amount: 200,
  description: 'Payment'
})

// Vérifier OTP et exécuter
const finalResponse = await transactionsAPI.verifyAndExecute({
  transactionId: response.data.transactionId,
  otp: '123456'
})
\`\`\`

## 7. Déploiement

### Development
\`\`\`bash
npm run dev
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
\`\`\`

### Production
\`\`\`bash
npm run build
npm start

# Mise à jour .env.local avec l'URL backend en production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
