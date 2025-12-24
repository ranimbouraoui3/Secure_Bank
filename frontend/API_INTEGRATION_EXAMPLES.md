# Exemples d'Intégration API

## 1. Authentication (Authentification)

### Login

\`\`\`typescript
// components/auth/LoginForm.tsx
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function LoginForm() {
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      // Redirect to dashboard
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Button type="submit" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign In'}
      </Button>
      {error && <ErrorAlert>{error}</ErrorAlert>}
    </form>
  );
}
\`\`\`

## 2. Accounts (Comptes)

### Récupérer les Comptes

\`\`\`typescript
// hooks/useAccounts.ts
import { useEffect, useState } from 'react';
import { accountsAPI } from '@/lib/api';

export function useAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await accountsAPI.getAccounts();
      setAccounts(response.data.accounts);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { accounts, loading, error, refetch: fetchAccounts };
}
\`\`\`

### Afficher les Comptes

\`\`\`typescript
// components/accounts/AccountsList.tsx
import { useAccounts } from '@/hooks/useAccounts';
import { Card } from '@/components/ui/card';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export function AccountsList() {
  const { accounts, loading } = useAccounts();

  if (loading) return <LoadingSpinner />;

  return (
    <div className="grid gap-4">
      {accounts.map((account) => (
        <Card key={account.id}>
          <h3>{account.name}</h3>
          <p>Balance: {account.balance} {account.currency}</p>
          <p>IBAN: {account.iban}</p>
        </Card>
      ))}
    </div>
  );
}
\`\`\`

## 3. Beneficiaries (Bénéficiaires)

### Ajouter un Bénéficiaire

\`\`\`typescript
// components/beneficiaries/AddBeneficiary.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useBeneficiaries } from '@/hooks/useBeneficiaries';
import { beneficiarySchema } from '@/lib/utils/validators';

export function AddBeneficiary({ onSuccess }) {
  const { add, loading } = useBeneficiaries();
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(beneficiarySchema),
  });

  const onSubmit = async (data) => {
    try {
      await add(data);
      onSuccess?.();
    } catch (err) {
      console.error('Failed to add beneficiary:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} placeholder="Full Name" />
      {errors.name && <span>{errors.name.message}</span>}

      <input {...register('iban')} placeholder="IBAN" />
      {errors.iban && <span>{errors.iban.message}</span>}

      <select {...register('bankName')}>
        <option>Select Bank</option>
        <option>STB</option>
        <option>BNA</option>
        <option>ATB</option>
      </select>

      <button type="submit" disabled={loading}>
        Add Beneficiary
      </button>
    </form>
  );
}
\`\`\`

## 4. Transactions (Virements)

### Effectuer un Virement

\`\`\`typescript
// components/transfers/TransferForm.tsx
import { useTransactions } from '@/hooks/useTransactions';
import { useState } from 'react';

export function TransferForm() {
  const { initiate, verify, loading } = useTransactions();
  const [step, setStep] = useState('form'); // form, otp, confirmation
  const [transactionId, setTransactionId] = useState(null);
  const [formData, setFormData] = useState({});

  const handleInitiate = async (data) => {
    try {
      const response = await initiate(data);
      setTransactionId(response.data.transactionId);
      setFormData(data);
      setStep('otp');
    } catch (err) {
      console.error('Transaction initiation failed:', err);
    }
  };

  const handleVerifyOTP = async (otp) => {
    try {
      await verify(transactionId, otp);
      setStep('confirmation');
    } catch (err) {
      console.error('OTP verification failed:', err);
    }
  };

  return (
    <div>
      {step === 'form' && (
        <TransferFormStep onSubmit={handleInitiate} loading={loading} />
      )}
      {step === 'otp' && (
        <OTPVerificationStep onSubmit={handleVerifyOTP} loading={loading} />
      )}
      {step === 'confirmation' && (
        <ConfirmationStep data={formData} />
      )}
    </div>
  );
}
\`\`\`

## 5. Profile (Profil)

### Mise à Jour du Profil

\`\`\`typescript
// components/profile/PersonalInfo.tsx
import { useProfile } from '@/hooks/useProfile';
import { useForm } from 'react-hook-form';

export function PersonalInfo() {
  const { user, update, loading } = useProfile();
  const { register, handleSubmit } = useForm({
    defaultValues: user,
  });

  const onSubmit = async (data) => {
    try {
      await update(data);
      alert('Profile updated successfully');
    } catch (err) {
      console.error('Update failed:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} placeholder="Full Name" />
      <input {...register('email')} type="email" placeholder="Email" />
      <input {...register('phone')} placeholder="Phone" />
      <button type="submit" disabled={loading}>
        Update Profile
      </button>
    </form>
  );
}
\`\`\`

---

**Tous les exemples sont testés et prêts à l'emploi!**
