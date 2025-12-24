# Documentation des Interfaces API et Hooks React

## Vue d'ensemble

Ce document décrit toutes les interfaces TypeScript et hooks React disponibles pour interagir avec le backend Django.

---

## Interfaces TypeScript

### 1. Authentification (2FA)

**Interface: `TwoFASetupResponse`**
\`\`\`typescript
interface TwoFASetupResponse {
  success: boolean
  qrCode?: string          // QR code pour scanner avec Google Authenticator
  secret?: string          // Secret TOTP pour configuration manuelle
  backupCodes?: string[]   // Codes de secours en cas de perte du téléphone
}
\`\`\`

**Hook React: `use2FA()`**
\`\`\`typescript
const { 
  isLoading,      // Indicateur de chargement
  error,          // Message d'erreur
  qrCode,         // QR code pour 2FA
  backupCodes,    // Codes de secours
  enable2FA,      // Fonction pour activer 2FA
  disable2FA,     // Fonction pour désactiver 2FA
  verify2FA       // Fonction pour vérifier le code 2FA
} = use2FA()

// Activer 2FA
await enable2FA()

// Désactiver 2FA
await disable2FA('123456')

// Vérifier code 2FA
await verify2FA('123456')
\`\`\`

---

### 2. Liste des Comptes Bancaires

**Interface: `BankAccount`**
\`\`\`typescript
interface BankAccount {
  id: string
  name: string
  balance: number
  iban: string
  accountType: "checking" | "savings" | "business"
  currency: string
  status: "active" | "inactive" | "blocked"
  createdAt: string
  lastUpdated: string
}
\`\`\`

**Hook React: `useAccounts()`**
\`\`\`typescript
const { 
  accounts,        // Liste des comptes
  isLoading,       // Indicateur de chargement
  error,           // Message d'erreur
  fetchAccounts,   // Recharger les comptes
  getAccountById   // Obtenir un compte spécifique
} = useAccounts()

// Récupérer tous les comptes
useEffect(() => {
  fetchAccounts()
}, [])
\`\`\`

---

### 3. Initier un Virement Bancaire

**Interface: `InitiateTransferRequest`**
\`\`\`typescript
interface InitiateTransferRequest {
  fromAccountId: string       // ID du compte source
  toBeneficiaryId?: string    // ID du bénéficiaire (optionnel)
  toIBAN?: string            // IBAN du bénéficiaire (si pas ID)
  amount: number             // Montant du virement
  description?: string       // Description (optionnel)
}
\`\`\`

**Interface: `InitiateTransferResponse`**
\`\`\`typescript
interface InitiateTransferResponse {
  success: boolean
  transferId: string         // ID du virement pour confirmation
  amount: number
  otpSent: boolean          // OTP envoyé par email
  message: string
  requiresOTP: boolean      // Nécessite validation OTP
}
\`\`\`

---

### 4. Valider un Virement par Code OTP

**Interface: `ConfirmTransferRequest`**
\`\`\`typescript
interface ConfirmTransferRequest {
  otp: string              // Code OTP à 6 chiffres
}
\`\`\`

**Interface: `ConfirmTransferResponse`**
\`\`\`typescript
interface ConfirmTransferResponse {
  success: boolean
  message: string
  transaction: Transaction  // Détails de la transaction complétée
}
\`\`\`

**Hook React Complet: `useTransfer()`**
\`\`\`typescript
const { 
  isLoading,           // Indicateur de chargement
  error,               // Message d'erreur
  transferId,          // ID du virement en attente
  requiresOTP,         // Indique si OTP est requis
  initiateTransfer,    // Étape 1: Initier le virement
  confirmTransfer,     // Étape 2: Confirmer avec OTP
  resendOTP,           // Renvoyer le code OTP
  resetTransfer        // Réinitialiser l'état
} = useTransfer()

// Exemple d'utilisation complète:

// Étape 1: Initier le virement
const handleInitiate = async () => {
  try {
    const result = await initiateTransfer({
      fromAccountId: 'account-123',
      toBeneficiaryId: 'beneficiary-456',
      amount: 500,
      description: 'Paiement facture'
    })
    
    if (result.requiresOTP) {
      // Afficher le formulaire OTP
      setShowOTPForm(true)
    }
  } catch (err) {
    console.error('Erreur:', error)
  }
}

// Étape 2: Confirmer avec OTP
const handleConfirm = async (otpCode: string) => {
  try {
    const result = await confirmTransfer(otpCode)
    console.log('Virement réussi!', result.transaction)
  } catch (err) {
    console.error('OTP invalide:', error)
  }
}

// Renvoyer OTP si nécessaire
const handleResendOTP = async () => {
  await resendOTP('user@example.com')
}
\`\`\`

---

## Exemple Complet d'Utilisation

### Composant React pour Virement Bancaire

\`\`\`typescript
import { useState } from 'react'
import { useTransfer } from '@/hooks/useTransfer'
import { useAccounts } from '@/hooks/useAccounts'

export function TransferForm() {
  const [step, setStep] = useState<'form' | 'otp'>('form')
  const [formData, setFormData] = useState({
    fromAccountId: '',
    toBeneficiaryId: '',
    amount: 0,
    description: ''
  })
  const [otpCode, setOtpCode] = useState('')

  const { accounts, fetchAccounts } = useAccounts()
  const { 
    isLoading, 
    error, 
    requiresOTP, 
    initiateTransfer, 
    confirmTransfer 
  } = useTransfer()

  // Charger les comptes au montage
  useEffect(() => {
    fetchAccounts()
  }, [])

  // Étape 1: Soumettre le formulaire
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const result = await initiateTransfer(formData)
      
      if (result.requiresOTP) {
        setStep('otp')
      }
    } catch (err) {
      console.error('Erreur lors de l\'initiation:', err)
    }
  }

  // Étape 2: Valider OTP
  const handleOTPSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const result = await confirmTransfer(otpCode)
      alert('Virement réussi! Référence: ' + result.transaction.referenceNumber)
      // Réinitialiser et retourner au dashboard
    } catch (err) {
      console.error('OTP invalide:', err)
    }
  }

  if (step === 'otp') {
    return (
      <form onSubmit={handleOTPSubmit}>
        <h2>Entrez le code OTP</h2>
        <p>Un code à 6 chiffres a été envoyé à votre email</p>
        
        <input
          type="text"
          value={otpCode}
          onChange={(e) => setOtpCode(e.target.value)}
          placeholder="123456"
          maxLength={6}
        />
        
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Validation...' : 'Confirmer le virement'}
        </button>
        
        {error && <p className="error">{error}</p>}
      </form>
    )
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Nouveau virement</h2>
      
      <select
        value={formData.fromAccountId}
        onChange={(e) => setFormData({...formData, fromAccountId: e.target.value})}
      >
        <option value="">Sélectionner un compte</option>
        {accounts.map(account => (
          <option key={account.id} value={account.id}>
            {account.name} - {account.balance} {account.currency}
          </option>
        ))}
      </select>

      <input
        type="number"
        value={formData.amount}
        onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value)})}
        placeholder="Montant"
      />

      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Traitement...' : 'Continuer'}
      </button>

      {error && <p className="error">{error}</p>}
    </form>
  )
}
\`\`\`

---

## Résumé des Hooks Disponibles

| Hook | Description | Fonctionnalités |
|------|-------------|-----------------|
| `use2FA()` | Gestion 2FA | enable, disable, verify |
| `useAccounts()` | Comptes bancaires | fetch, getById, update |
| `useBeneficiaries()` | Bénéficiaires | fetch, add, update, delete |
| `useTransfer()` | Virements | initiate, confirm, resendOTP |
| `useTransactions()` | Historique | fetch, filter, export |
| `useProfile()` | Profil utilisateur | fetch, update, changePassword |
| `useSecurityEvents()` | Événements sécurité | loginEvents, failedAttempts |

---

## Notes Importantes

1. **OTP obligatoire**: Pour les virements > 1000 TND, un code OTP est automatiquement envoyé
2. **ACID Transactions**: Tous les virements sont traités avec garantie ACID côté backend
3. **Email de confirmation**: Un email est automatiquement envoyé après chaque virement réussi
4. **Rate limiting**: Maximum 5 tentatives OTP avant blocage temporaire
5. **Expiration OTP**: Les codes OTP expirent après 5 minutes

Toutes les interfaces sont disponibles dans `lib/types/api-types.ts` et tous les hooks dans `hooks/`.
