// ============================================
// TYPES & INTERFACES FOR API RESPONSES
// ============================================

// Authentication Types
export interface User {
  id: string
  email: string
  name: string
  phone: string
  isVerified: boolean
  twoFactorEnabled: boolean
  createdAt: string
  lastLogin?: string
}

export interface LoginResponse {
  success: boolean
  token: string
  refreshToken: string
  user: User
}

export interface RegisterResponse {
  success: boolean
  message: string
  userId: string
  email: string
}

export interface OTPResponse {
  success: boolean
  message: string
  expiresIn: number
}

export interface TwoFASetupResponse {
  success: boolean
  qrCode?: string
  secret?: string
  backupCodes?: string[]
}

// Account Types
export interface BankAccount {
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

export interface AccountBalance {
  balance: number
  availableBalance: number
  currency: string
  lastUpdated: string
}

export interface AccountStatement {
  transactions: Transaction[]
  startDate: string
  endDate: string
  totalCredits: number
  totalDebits: number
}

// Beneficiary Types
export interface Beneficiary {
  id: string
  name: string
  iban: string
  bankName: string
  status: "verified" | "pending_verification" | "blocked"
  addedAt: string
  lastUsed?: string
}

export interface AddBeneficiaryRequest {
  name: string
  iban: string
  bankName: string
}

// Transaction Types
export interface Transaction {
  id: string
  type: "sent" | "received"
  amount: number
  currency: string
  beneficiary: string
  beneficiaryIBAN: string
  fromAccount: string
  date: string
  status: "completed" | "pending" | "failed" | "cancelled"
  referenceNumber: string
  timestamp: string
  description?: string
  confirmationEmailSent?: boolean
}

export interface InitiateTransferRequest {
  fromAccountId: string
  toBeneficiaryId?: string
  toIBAN?: string
  amount: number
  description?: string
}

export interface InitiateTransferResponse {
  success: boolean
  transferId: string
  amount: number
  otpSent: boolean
  message: string
  requiresOTP: boolean
}

export interface ConfirmTransferRequest {
  otp: string
}

export interface ConfirmTransferResponse {
  success: boolean
  message: string
  transaction: Transaction
}

// Profile Types
export interface Profile {
  user: User
  preferences: {
    language: string
    notifications: boolean
    emailAlerts: boolean
  }
}

export interface UpdateProfileRequest {
  email?: string
  name?: string
  phone?: string
}

export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

// Security Types
export interface LoginEvent {
  id: string
  timestamp: string
  ipAddress: string
  userAgent: string
  location?: string
  success: boolean
}

export interface FailedAttempt {
  timestamp: string
  ipAddress: string
  reason: string
}

// API Response Wrapper
export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// Filter/Query Parameters
export interface TransactionFilters {
  accountId?: string
  type?: "sent" | "received"
  status?: "completed" | "pending" | "failed"
  startDate?: string
  endDate?: string
  limit?: number
  offset?: number
}

export interface PaginationParams {
  limit?: number
  offset?: number
}
