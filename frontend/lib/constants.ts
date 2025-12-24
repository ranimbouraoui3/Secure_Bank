// Validation regex patterns
export const VALIDATION = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  IBAN: /^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$/,
  PHONE_TN: /^216[0-9]{8}$|^[0-9]{8}$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  OTP: /^\d{6}$/,
}

// API response status
export const API_STATUS = {
  SUCCESS: "success",
  ERROR: "error",
  LOADING: "loading",
}

// Transaction types
export const TRANSACTION_TYPE = {
  SENT: "sent",
  RECEIVED: "received",
}

// Transaction status
export const TRANSACTION_STATUS = {
  PENDING: "pending",
  COMPLETED: "completed",
  FAILED: "failed",
}
