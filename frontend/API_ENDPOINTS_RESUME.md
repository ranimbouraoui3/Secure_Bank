# 📋 API Endpoints Resume - Frontend React Integration

## Overview

This document provides a comprehensive summary of all API endpoints implemented in the React frontend to communicate with the Django REST backend for the Secure Banking Application.

---

## 1. AUTHENTICATION ENDPOINTS

### 1.1 Register
\`\`\`typescript
authAPI.register({
  email: string,
  password: string,
  name: string,
  phone: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/register`
- **Purpose**: Create a new user account
- **Response**: User object with tokens

### 1.2 Login
\`\`\`typescript
authAPI.login({
  email: string,
  password: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/login`
- **Purpose**: Authenticate user and get tokens
- **Response**: `{ token, refreshToken, user }`

### 1.3 Request OTP
\`\`\`typescript
authAPI.requestOTP({
  email: string,
  type: "login" | "transfer" | "password-reset"
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/otp/send`
- **Purpose**: Send OTP to user email
- **Response**: `{ success: true, expiresIn: 300 }`

### 1.4 Verify OTP
\`\`\`typescript
authAPI.verifyOTP({
  email: string,
  otp: string,
  type: "login" | "transfer" | "password-reset"
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/otp/verify`
- **Purpose**: Verify OTP code for 2FA
- **Response**: `{ success: true, token: string }`

### 1.5 Refresh Token
\`\`\`typescript
authAPI.refreshToken(refreshToken: string)
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/refresh`
- **Purpose**: Get new access token using refresh token
- **Response**: `{ token: string }`

### 1.6 Logout
\`\`\`typescript
authAPI.logout(refreshToken: string)
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/logout`
- **Purpose**: Logout user and blacklist token
- **Response**: `{ success: true }`

### 1.7 Enable 2FA
\`\`\`typescript
authAPI.enableTwoFA()
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/2fa/enable`
- **Purpose**: Enable two-factor authentication
- **Response**: `{ secret, qrCode }`

### 1.8 Disable 2FA
\`\`\`typescript
authAPI.disableTwoFA({
  password: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/2fa/disable`
- **Purpose**: Disable two-factor authentication
- **Response**: `{ success: true }`

### 1.9 Verify 2FA Setup
\`\`\`typescript
authAPI.verifyTwoFA({
  otp: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/auth/2fa/verify`
- **Purpose**: Verify 2FA setup with OTP
- **Response**: `{ success: true }`

---

## 2. ACCOUNTS ENDPOINTS

### 2.1 Get All Accounts
\`\`\`typescript
accountsAPI.getAccounts()
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/accounts`
- **Purpose**: Fetch all user bank accounts
- **Response**: `{ accounts: BankAccount[] }`

### 2.2 Get Account Detail
\`\`\`typescript
accountsAPI.getAccountDetail(accountId: string)
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/accounts/{accountId}`
- **Purpose**: Get specific account details
- **Response**: `{ account: BankAccount }`

### 2.3 Get Account Balance
\`\`\`typescript
accountsAPI.getAccountBalance(accountId: string)
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/accounts/{accountId}/balance`
- **Purpose**: Get current account balance
- **Response**: `{ balance: number, currency: string }`

### 2.4 Get Account Statement
\`\`\`typescript
accountsAPI.getAccountStatement(accountId: string, {
  startDate?: string,
  endDate?: string,
  limit?: number
})
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/accounts/{accountId}/statement`
- **Purpose**: Get account transactions/statement
- **Response**: `{ transactions: Transaction[] }`

### 2.5 Update Account
\`\`\`typescript
accountsAPI.updateAccount(accountId: string, {
  name: string
})
\`\`\`
- **Method**: PUT
- **Endpoint**: `/api/accounts/{accountId}`
- **Purpose**: Update account nickname
- **Response**: `{ account: BankAccount }`

---

## 3. BENEFICIARIES ENDPOINTS

### 3.1 Get All Beneficiaries
\`\`\`typescript
beneficiariesAPI.getBeneficiaries()
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/beneficiaries`
- **Purpose**: Fetch all user beneficiaries
- **Response**: `{ beneficiaries: Beneficiary[] }`

### 3.2 Get Beneficiary Detail
\`\`\`typescript
beneficiariesAPI.getBeneficiary(beneficiaryId: string)
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/beneficiaries/{beneficiaryId}`
- **Purpose**: Get specific beneficiary details
- **Response**: `{ beneficiary: Beneficiary }`

### 3.3 Add Beneficiary
\`\`\`typescript
beneficiariesAPI.addBeneficiary({
  name: string,
  iban: string,
  bankName: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/beneficiaries`
- **Purpose**: Add a new beneficiary
- **Response**: `{ beneficiary: Beneficiary, status: "pending_verification" }`

### 3.4 Update Beneficiary
\`\`\`typescript
beneficiariesAPI.updateBeneficiary(beneficiaryId: string, {
  name?: string,
  bankName?: string
})
\`\`\`
- **Method**: PUT
- **Endpoint**: `/api/beneficiaries/{beneficiaryId}`
- **Purpose**: Update beneficiary information
- **Response**: `{ beneficiary: Beneficiary }`

### 3.5 Delete Beneficiary
\`\`\`typescript
beneficiariesAPI.deleteBeneficiary(beneficiaryId: string)
\`\`\`
- **Method**: DELETE
- **Endpoint**: `/api/beneficiaries/{beneficiaryId}`
- **Purpose**: Remove a beneficiary
- **Response**: `{ success: true }`

### 3.6 Verify Beneficiary
\`\`\`typescript
beneficiariesAPI.verifyBeneficiary(beneficiaryId: string)
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/beneficiaries/{beneficiaryId}/verify`
- **Purpose**: Verify beneficiary account
- **Response**: `{ status: "verified" }`

---

## 4. TRANSACTIONS ENDPOINTS

### 4.1 Get Transactions
\`\`\`typescript
transactionsAPI.getTransactions({
  accountId?: string,
  type?: "sent" | "received",
  status?: "completed" | "pending" | "failed",
  startDate?: string,
  endDate?: string,
  limit?: number,
  offset?: number
})
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/transactions`
- **Purpose**: Fetch transaction history with filters
- **Response**: `{ transactions: Transaction[], total: number }`

### 4.2 Get Transaction Detail
\`\`\`typescript
transactionsAPI.getTransactionDetail(transactionId: string)
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/transactions/{transactionId}`
- **Purpose**: Get detailed transaction information
- **Response**: `{ transaction: Transaction }`

### 4.3 Initiate Transaction
\`\`\`typescript
transactionsAPI.initiateTransaction({
  fromAccountId: string,
  toBeneficiaryId?: string,
  toIBAN?: string,
  amount: number,
  description?: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/transactions/initiate`
- **Purpose**: Start a transfer process (sends OTP)
- **Response**: `{ transactionId, otpSent: true, expiresIn: 300 }`

### 4.4 Verify and Execute Transaction
\`\`\`typescript
transactionsAPI.verifyAndExecute({
  transactionId: string,
  otp: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/transactions/verify-and-execute`
- **Purpose**: Verify OTP and complete transfer (ACID transaction)
- **Response**: `{ transaction: Transaction, confirmationEmailSent: true }`

### 4.5 Get Pending Transaction
\`\`\`typescript
transactionsAPI.getPendingTransaction(transactionId: string)
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/transactions/{transactionId}/pending`
- **Purpose**: Get pending transaction details
- **Response**: `{ transaction: PendingTransaction }`

### 4.6 Cancel Transaction
\`\`\`typescript
transactionsAPI.cancelTransaction(transactionId: string)
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/transactions/{transactionId}/cancel`
- **Purpose**: Cancel a pending transaction
- **Response**: `{ success: true }`

### 4.7 Retry Transaction
\`\`\`typescript
transactionsAPI.retryTransaction(transactionId: string)
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/transactions/{transactionId}/retry`
- **Purpose**: Retry a failed transaction
- **Response**: `{ transaction: Transaction }`

### 4.8 Export Transactions
\`\`\`typescript
transactionsAPI.exportTransactions("csv" | "pdf", {
  startDate?: string,
  endDate?: string
})
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/transactions/export`
- **Purpose**: Export transactions as CSV or PDF
- **Response**: Blob data

---

## 5. PROFILE ENDPOINTS

### 5.1 Get Profile
\`\`\`typescript
profileAPI.getProfile()
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/profile`
- **Purpose**: Get current user profile
- **Response**: `{ user: User }`

### 5.2 Update Profile
\`\`\`typescript
profileAPI.updateProfile({
  email?: string,
  name?: string,
  phone?: string
})
\`\`\`
- **Method**: PUT
- **Endpoint**: `/api/profile`
- **Purpose**: Update user information
- **Response**: `{ user: User }`

### 5.3 Change Password
\`\`\`typescript
profileAPI.changePassword({
  currentPassword: string,
  newPassword: string,
  confirmPassword: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/profile/change-password`
- **Purpose**: Change user password
- **Response**: `{ success: true }`

### 5.4 Request Email Verification
\`\`\`typescript
profileAPI.requestEmailVerification()
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/profile/email/verify-request`
- **Purpose**: Request email verification OTP
- **Response**: `{ success: true, expiresIn: 300 }`

### 5.5 Verify Email
\`\`\`typescript
profileAPI.verifyEmail({
  otp: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/profile/email/verify`
- **Purpose**: Verify email with OTP
- **Response**: `{ success: true, emailVerified: true }`

### 5.6 Update Phone Number
\`\`\`typescript
profileAPI.updatePhoneNumber({
  phone: string
})
\`\`\`
- **Method**: PUT
- **Endpoint**: `/api/profile/phone`
- **Purpose**: Update phone number
- **Response**: `{ phone: string }`

### 5.7 Get Last Login
\`\`\`typescript
profileAPI.getLastLogin()
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/profile/last-login`
- **Purpose**: Get last login information
- **Response**: `{ lastLogin: string, ipAddress: string }`

### 5.8 Logout All Devices
\`\`\`typescript
profileAPI.logoutAllDevices()
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/profile/logout-all-devices`
- **Purpose**: Logout user from all sessions
- **Response**: `{ success: true }`

### 5.9 Get Settings
\`\`\`typescript
profileAPI.getSettings()
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/profile/settings`
- **Purpose**: Get account settings
- **Response**: `{ settings: AccountSettings }`

### 5.10 Update Settings
\`\`\`typescript
profileAPI.updateSettings({
  notificationsEmail?: boolean,
  notificationsSMS?: boolean
})
\`\`\`
- **Method**: PUT
- **Endpoint**: `/api/profile/settings`
- **Purpose**: Update account settings
- **Response**: `{ settings: AccountSettings }`

### 5.11 Delete Account
\`\`\`typescript
profileAPI.deleteAccount({
  password: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/profile/delete`
- **Purpose**: Delete user account permanently
- **Response**: `{ success: true }`

---

## 6. OTP ENDPOINTS

### 6.1 Send OTP
\`\`\`typescript
otpAPI.sendOTP({
  email: string,
  type: "login" | "transfer" | "password-reset" | "email-verification"
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/otp/send`
- **Purpose**: Send OTP to email
- **Response**: `{ success: true, expiresIn: 300 }`

### 6.2 Verify OTP
\`\`\`typescript
otpAPI.verifyOTP({
  email: string,
  otp: string,
  type: "login" | "transfer" | "password-reset" | "email-verification"
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/otp/verify`
- **Purpose**: Verify OTP code
- **Response**: `{ success: true, token?: string }`

### 6.3 Resend OTP
\`\`\`typescript
otpAPI.resendOTP({
  email: string,
  type: string
})
\`\`\`
- **Method**: POST
- **Endpoint**: `/api/otp/resend`
- **Purpose**: Resend OTP if not received
- **Response**: `{ success: true, expiresIn: 300 }`

### 6.4 Get OTP Status
\`\`\`typescript
otpAPI.getOTPStatus(email: string)
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/otp/status/{email}`
- **Purpose**: Check OTP status (debugging)
- **Response**: `{ status: "sent" | "verified" | "expired" }`

---

## 7. AUDIT ENDPOINTS

### 7.1 Get Audit Logs
\`\`\`typescript
auditAPI.getAuditLogs({
  userId?: string,
  action?: string,
  startDate?: string,
  endDate?: string,
  limit?: number,
  offset?: number
})
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/audit/logs`
- **Purpose**: Get audit logs with filters
- **Response**: `{ logs: AuditLog[], total: number }`

### 7.2 Get Audit Log
\`\`\`typescript
auditAPI.getAuditLog(logId: string)
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/audit/logs/{logId}`
- **Purpose**: Get specific audit log entry
- **Response**: `{ log: AuditLog }`

### 7.3 Get Activity Summary
\`\`\`typescript
auditAPI.getActivitySummary()
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/audit/activity-summary`
- **Purpose**: Get user activity summary
- **Response**: `{ totalLogins, lastLogin, suspiciousActivities }`

### 7.4 Get Security Events
\`\`\`typescript
auditAPI.getSecurityEvents({
  limit?: number,
  offset?: number
})
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/audit/security-events`
- **Purpose**: Get security-related events
- **Response**: `{ events: SecurityEvent[], total: number }`

### 7.5 Export Audit Logs
\`\`\`typescript
auditAPI.exportAuditLogs("csv" | "pdf", {
  startDate?: string,
  endDate?: string
})
\`\`\`
- **Method**: GET
- **Endpoint**: `/api/audit/export`
- **Purpose**: Export audit logs as file
- **Response**: Blob data

---

## Summary Table

| Category | Total Endpoints | Purpose |
|----------|-----------------|---------|
| Authentication | 9 | User registration, login, 2FA, tokens |
| Accounts | 5 | Bank account management |
| Beneficiaries | 6 | Beneficiary CRUD operations |
| Transactions | 8 | Transfer, history, ACID operations |
| Profile | 11 | User profile and settings |
| OTP | 4 | OTP generation and verification |
| Audit | 5 | Logging and activity tracking |
| **TOTAL** | **48** | **Complete banking application** |

---

## Security Features

Each endpoint includes:
- ✅ JWT Bearer token authentication
- ✅ CORS headers
- ✅ Rate limiting
- ✅ Input validation
- ✅ Error handling
- ✅ Audit logging
- ✅ HTTPS/TLS encryption

---

## Error Handling

All endpoints follow standard error response format:
\`\`\`typescript
{
  success: false,
  error: "Error message",
  status: 400,
  details?: { field: "error details" }
}
\`\`\`

---

## Usage Example

\`\`\`typescript
import { authAPI, transactionsAPI, handleAPIError } from "@/lib/api"

// Login
try {
  const response = await authAPI.login({
    email: "user@example.com",
    password: "password"
  })
  localStorage.setItem("token", response.data.token)
} catch (error) {
  const err = handleAPIError(error)
  console.log(err.error)
}

// Initiate Transfer
try {
  const response = await transactionsAPI.initiateTransaction({
    fromAccountId: "account-id",
    toBeneficiaryId: "beneficiary-id",
    amount: 250.00,
    description: "Payment"
  })
  // OTP sent, show OTP verification modal
} catch (error) {
  const err = handleAPIError(error)
}
\`\`\`

---

**Last Updated**: December 2025
**Status**: Complete and ready for Django backend integration
**Total Endpoints**: 48
**Frontend Framework**: Next.js 16 with React
**Backend Framework**: Django REST Framework
