// lib/constants/index.ts - Application constants
export const APP_NAME = "Secure Banking"

export const TRANSACTION_TYPES = {
  SENT: "sent",
  RECEIVED: "received",
}

export const TRANSACTION_STATUS = {
  PENDING: "pending",
  COMPLETED: "completed",
  FAILED: "failed",
}

export const ACCOUNT_TYPES = {
  CHECKING: "checking",
  SAVINGS: "savings",
}

export const OTP_EXPIRY = 300 // 5 minutes in seconds

export const RATE_LIMITS = {
  LOGIN_ATTEMPTS: 5,
  LOGIN_LOCKOUT_TIME: 900, // 15 minutes in seconds
}
