# Secure Banking Frontend - API Endpoints Specification

Complete list of all API endpoints required for the backend implementation.

---

## 1. AUTHENTICATION

### [1.1] USER REGISTRATION
**METHOD:** POST  
**ROUTE:** `/api/auth/register`

**REQUEST:**
\`\`\`json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "phone": "+216 90123456"
}
\`\`\`

**SUCCESS RESPONSE (201 Created):**
\`\`\`json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+216 90123456",
  "created_at": "2024-01-15T10:30:00Z",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid email format"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Email already registered"
  }
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Password must be 8+ characters with uppercase, lowercase, digit, and special character"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid phone number format"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to create user account"
  }
  \`\`\`

---

### [1.2] USER LOGIN
**METHOD:** POST  
**ROUTE:** `/api/auth/login`

**REQUEST:**
\`\`\`json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
\`\`\`

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+216 90123456",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_expires_in": 3600
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Email and password required"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Invalid credentials"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Authentication failed"
  }
  \`\`\`

---

### [1.3] REFRESH TOKEN
**METHOD:** POST  
**ROUTE:** `/api/auth/refresh-token`

**REQUEST:**
\`\`\`json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
\`\`\`

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_expires_in": 3600
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Invalid or expired refresh token"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Token refresh failed"
  }
  \`\`\`

---

### [1.4] USER LOGOUT
**METHOD:** POST  
**ROUTE:** `/api/auth/logout`

**REQUEST:**
\`\`\`json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
\`\`\`

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "message": "Logged out successfully"
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Logout failed"
  }
  \`\`\`

---

## 2. USER PROFILE

### [2.1] GET USER PROFILE
**METHOD:** GET  
**ROUTE:** `/api/users/profile`

**REQUEST:** (No body, pass access_token in Authorization header)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+216 90123456",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:25:00Z",
  "two_fa_enabled": false
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **404 Not Found:**
  \`\`\`json
  {
    "error": "User not found"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch user profile"
  }
  \`\`\`

---

### [2.2] UPDATE USER PROFILE
**METHOD:** PATCH  
**ROUTE:** `/api/users/profile`

**REQUEST:**
\`\`\`json
{
  "name": "John Doe Updated",
  "phone": "+216 90654321"
}
\`\`\`

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe Updated",
  "phone": "+216 90654321",
  "updated_at": "2024-01-20T14:30:00Z"
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid phone number format"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to update profile"
  }
  \`\`\`

---

### [2.3] CHANGE PASSWORD
**METHOD:** POST  
**ROUTE:** `/api/users/change-password`

**REQUEST:**
\`\`\`json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
\`\`\`

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "message": "Password changed successfully"
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Password must be 8+ characters with uppercase, lowercase, digit, and special character"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Current password is incorrect"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to change password"
  }
  \`\`\`

---

### [2.4] ENABLE 2FA (TWO-FACTOR AUTHENTICATION)
**METHOD:** POST  
**ROUTE:** `/api/users/2fa/enable`

**REQUEST:** (No body)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "message": "2FA enabled successfully",
  "qr_code": "data:image/png;base64,iVBORw0KG...",
  "secret": "JBSWY3DPEBLW64TMMQ"
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "2FA already enabled"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to enable 2FA"
  }
  \`\`\`

---

### [2.5] DISABLE 2FA
**METHOD:** POST  
**ROUTE:** `/api/users/2fa/disable`

**REQUEST:**
\`\`\`json
{
  "otp_code": "123456"
}
\`\`\`

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "message": "2FA disabled successfully"
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid OTP code"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "2FA not enabled"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to disable 2FA"
  }
  \`\`\`

---

## 3. ACCOUNTS

### [3.1] LIST ALL ACCOUNTS
**METHOD:** GET  
**ROUTE:** `/api/accounts`

**REQUEST:** (No body, pass access_token in Authorization header)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "accounts": [
    {
      "id": "acc_001",
      "name": "Main Account",
      "balance": 5250.75,
      "currency": "TND",
      "iban": "TN5910006035183738981234",
      "account_type": "checking",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "acc_002",
      "name": "Savings Account",
      "balance": 12450.00,
      "currency": "TND",
      "iban": "TN5910006035183738981235",
      "account_type": "savings",
      "status": "active",
      "created_at": "2024-01-05T00:00:00Z"
    }
  ],
  "total_accounts": 2
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch accounts"
  }
  \`\`\`

---

### [3.2] GET ACCOUNT DETAILS
**METHOD:** GET  
**ROUTE:** `/api/accounts/:account_id`

**REQUEST:** (No body, pass access_token in Authorization header)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "id": "acc_001",
  "name": "Main Account",
  "balance": 5250.75,
  "currency": "TND",
  "iban": "TN5910006035183738981234",
  "account_type": "checking",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "last_transaction": "2024-01-20T14:00:00Z"
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **404 Not Found:**
  \`\`\`json
  {
    "error": "Account not found"
  }
  \`\`\`
- **403 Forbidden:**
  \`\`\`json
  {
    "error": "You do not have access to this account"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch account details"
  }
  \`\`\`

---

## 4. BENEFICIARIES

### [4.1] LIST ALL BENEFICIARIES
**METHOD:** GET  
**ROUTE:** `/api/beneficiaries`

**REQUEST:** (No body, pass access_token in Authorization header)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "beneficiaries": [
    {
      "id": "bene_001",
      "name": "Ahmed Ben Ali",
      "iban": "TN5910006035183738981236",
      "bank_name": "STB",
      "created_at": "2024-01-10T00:00:00Z"
    },
    {
      "id": "bene_002",
      "name": "Fatima Khouja",
      "iban": "TN5910006035183738981237",
      "bank_name": "BNA",
      "created_at": "2024-01-12T00:00:00Z"
    }
  ],
  "total_beneficiaries": 2
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch beneficiaries"
  }
  \`\`\`

---

### [4.2] ADD BENEFICIARY
**METHOD:** POST  
**ROUTE:** `/api/beneficiaries`

**REQUEST:**
\`\`\`json
{
  "name": "Mohamed Salah",
  "iban": "TN5910006035183738981238",
  "bank_name": "BH Bank"
}
\`\`\`

**SUCCESS RESPONSE (201 Created):**
\`\`\`json
{
  "id": "bene_003",
  "name": "Mohamed Salah",
  "iban": "TN5910006035183738981238",
  "bank_name": "BH Bank",
  "created_at": "2024-01-20T15:00:00Z"
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Name, IBAN, and bank name are required"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid IBAN format"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Beneficiary with this IBAN already exists"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to add beneficiary"
  }
  \`\`\`

---

### [4.3] DELETE BENEFICIARY
**METHOD:** DELETE  
**ROUTE:** `/api/beneficiaries/:beneficiary_id`

**REQUEST:** (No body, pass access_token in Authorization header)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "message": "Beneficiary deleted successfully"
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **404 Not Found:**
  \`\`\`json
  {
    "error": "Beneficiary not found"
  }
  \`\`\`
- **403 Forbidden:**
  \`\`\`json
  {
    "error": "You do not have permission to delete this beneficiary"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to delete beneficiary"
  }
  \`\`\`

---

## 5. TRANSFERS & OTP

### [5.1] INITIATE TRANSFER
**METHOD:** POST  
**ROUTE:** `/api/transfers/initiate`

**REQUEST:**
\`\`\`json
{
  "from_account_id": "acc_001",
  "to_beneficiary_id": "bene_001",
  "amount": 500.00,
  "description": "Payment for services"
}
\`\`\`

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "transfer_id": "txn_001",
  "from_account": "acc_001",
  "to_beneficiary": "bene_001",
  "amount": 500.00,
  "currency": "TND",
  "description": "Payment for services",
  "status": "pending_otp",
  "created_at": "2024-01-20T15:30:00Z",
  "otp_required": true,
  "otp_sent_to": "user@example.com"
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "All fields are required"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid amount (must be between 0.01 and 1,000,000.00 TND)"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Insufficient balance"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Daily transfer limit exceeded"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **404 Not Found:**
  \`\`\`json
  {
    "error": "Account or beneficiary not found"
  }
  \`\`\`
- **403 Forbidden:**
  \`\`\`json
  {
    "error": "You do not have access to this account"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to initiate transfer"
  }
  \`\`\`

---

### [5.2] CONFIRM TRANSFER WITH OTP
**METHOD:** POST  
**ROUTE:** `/api/transfers/:transfer_id/confirm-otp`

**REQUEST:**
\`\`\`json
{
  "otp_code": "123456"
}
\`\`\`

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "transfer_id": "txn_001",
  "from_account": "acc_001",
  "to_beneficiary": "bene_001",
  "amount": 500.00,
  "currency": "TND",
  "status": "completed",
  "completed_at": "2024-01-20T15:35:00Z",
  "confirmation_number": "CONF-2024-001"
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "OTP code is required"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid or expired OTP code"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Maximum OTP attempts exceeded"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **404 Not Found:**
  \`\`\`json
  {
    "error": "Transfer not found"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Transfer already completed"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to confirm transfer"
  }
  \`\`\`

---

### [5.3] GET TRANSFER STATUS
**METHOD:** GET  
**ROUTE:** `/api/transfers/:transfer_id/status`

**REQUEST:** (No body, pass access_token in Authorization header)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "transfer_id": "txn_001",
  "from_account": "acc_001",
  "to_beneficiary": "bene_001",
  "amount": 500.00,
  "currency": "TND",
  "status": "completed",
  "created_at": "2024-01-20T15:30:00Z",
  "completed_at": "2024-01-20T15:35:00Z",
  "confirmation_number": "CONF-2024-001"
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **404 Not Found:**
  \`\`\`json
  {
    "error": "Transfer not found"
  }
  \`\`\`
- **403 Forbidden:**
  \`\`\`json
  {
    "error": "You do not have access to this transfer"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch transfer status"
  }
  \`\`\`

---

## 6. TRANSACTIONS (HISTORY)

### [6.1] LIST TRANSACTIONS
**METHOD:** GET  
**ROUTE:** `/api/transactions?account_id=acc_001&type=all&start_date=2024-01-01&end_date=2024-01-31&limit=20&offset=0`

**REQUEST:** (No body, pass access_token in Authorization header)

**Query Parameters:**
- `account_id` (optional): Filter by account ID
- `type` (optional): Filter by transaction type - `all`, `sent`, `received`
- `start_date` (optional): ISO-8601 format (e.g., 2024-01-01)
- `end_date` (optional): ISO-8601 format (e.g., 2024-01-31)
- `limit` (optional): Number of results (default 20, max 100)
- `offset` (optional): Pagination offset (default 0)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "transactions": [
    {
      "id": "txn_001",
      "account_id": "acc_001",
      "type": "sent",
      "amount": 500.00,
      "currency": "TND",
      "beneficiary_name": "Ahmed Ben Ali",
      "beneficiary_iban": "TN5910006035183738981236",
      "description": "Payment for services",
      "status": "completed",
      "created_at": "2024-01-20T15:35:00Z",
      "reference_number": "CONF-2024-001"
    },
    {
      "id": "txn_002",
      "account_id": "acc_001",
      "type": "received",
      "amount": 1000.00,
      "currency": "TND",
      "sender_name": "Fatima Khouja",
      "sender_iban": "TN5910006035183738981237",
      "description": "Salary",
      "status": "completed",
      "created_at": "2024-01-19T09:00:00Z",
      "reference_number": "CONF-2024-002"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
\`\`\`

**ERROR RESPONSES:**
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid date format (use ISO-8601)"
  }
  \`\`\`
- **400 Bad Request:**
  \`\`\`json
  {
    "error": "Invalid query parameters"
  }
  \`\`\`
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **404 Not Found:**
  \`\`\`json
  {
    "error": "Account not found"
  }
  \`\`\`
- **403 Forbidden:**
  \`\`\`json
  {
    "error": "You do not have access to this account"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch transactions"
  }
  \`\`\`

---

## 7. NOTIFICATIONS

### [7.1] LIST SENT NOTIFICATIONS (EMAILS)
**METHOD:** GET  
**ROUTE:** `/api/notifications?limit=20&offset=0`

**REQUEST:** (No body, pass access_token in Authorization header)

**Query Parameters:**
- `limit` (optional): Number of results (default 20, max 100)
- `offset` (optional): Pagination offset (default 0)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "notifications": [
    {
      "id": "notif_001",
      "type": "transfer_confirmation",
      "recipient_email": "user@example.com",
      "subject": "Transfer Confirmation",
      "message": "Your transfer of 500.00 TND to Ahmed Ben Ali has been completed.",
      "status": "sent",
      "sent_at": "2024-01-20T15:35:00Z"
    },
    {
      "id": "notif_002",
      "type": "login_alert",
      "recipient_email": "user@example.com",
      "subject": "New Login Detected",
      "message": "A new login was detected on your account from IP address 192.168.1.1",
      "status": "sent",
      "sent_at": "2024-01-20T14:00:00Z"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch notifications"
  }
  \`\`\`

---

## 8. SECURITY & LOGS

### [8.1] LIST LOGIN EVENTS
**METHOD:** GET  
**ROUTE:** `/api/security/login-events?limit=20&offset=0`

**REQUEST:** (No body, pass access_token in Authorization header)

**Query Parameters:**
- `limit` (optional): Number of results (default 20, max 100)
- `offset` (optional): Pagination offset (default 0)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "login_events": [
    {
      "id": "login_001",
      "user_id": "user_123",
      "ip_address": "192.168.1.100",
      "device": "Chrome on Windows",
      "location": "Tunis, Tunisia",
      "status": "successful",
      "login_at": "2024-01-20T14:25:00Z"
    },
    {
      "id": "login_002",
      "user_id": "user_123",
      "ip_address": "10.0.0.50",
      "device": "Firefox on Ubuntu",
      "location": "Sousse, Tunisia",
      "status": "successful",
      "login_at": "2024-01-19T09:15:00Z"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch login events"
  }
  \`\`\`

---

### [8.2] LIST FAILED LOGIN ATTEMPTS
**METHOD:** GET  
**ROUTE:** `/api/security/failed-attempts?limit=20&offset=0`

**REQUEST:** (No body, pass access_token in Authorization header)

**Query Parameters:**
- `limit` (optional): Number of results (default 20, max 100)
- `offset` (optional): Pagination offset (default 0)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "failed_attempts": [
    {
      "id": "fail_001",
      "user_id": "user_123",
      "email": "user@example.com",
      "ip_address": "203.0.113.45",
      "device": "Unknown",
      "reason": "Invalid password",
      "attempted_at": "2024-01-20T14:20:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to fetch failed login attempts"
  }
  \`\`\`

---

### [8.3] LOGOUT FROM ALL DEVICES
**METHOD:** POST  
**ROUTE:** `/api/security/logout-all-devices`

**REQUEST:** (No body, pass access_token in Authorization header)

**SUCCESS RESPONSE (200 OK):**
\`\`\`json
{
  "message": "Successfully logged out from all devices"
}
\`\`\`

**ERROR RESPONSES:**
- **401 Unauthorized:**
  \`\`\`json
  {
    "error": "Unauthorized"
  }
  \`\`\`
- **500 Server Error:**
  \`\`\`json
  {
    "error": "Failed to logout from all devices"
  }
  \`\`\`

---

## GENERAL NOTES

### Authentication Header Format
All endpoints (except `/api/auth/login`, `/api/auth/register`, and `/api/auth/refresh-token`) require:
\`\`\`
Authorization: Bearer <access_token>
\`\`\`

### Response Status Codes Summary
- **200 OK**: Successful GET/POST/PATCH request
- **201 Created**: Successful resource creation
- **400 Bad Request**: Invalid input or validation error
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: User lacks permission for resource
- **404 Not Found**: Resource does not exist
- **500 Server Error**: Server-side error

### Validation Rules
- **Email**: Standard email format (user@domain.com)
- **Password**: Minimum 8 characters, must include uppercase, lowercase, digit, and special character
- **Phone**: Tunisian format (+216 XXXXXXXX or XXXXXXXX after +216)
- **IBAN**: Format TN59 followed by alphanumeric characters (total 24 characters)
- **Amount**: Decimal format with max 2 decimal places, range 0.01 to 1,000,000.00 TND
- **Dates**: ISO-8601 format (YYYY-MM-DDTHH:mm:ssZ)

### OTP Security
- OTP codes are 6 digits
- OTP valid for 10 minutes
- Maximum 3 failed attempts before cooldown
- OTP sent via email to registered user email

### Rate Limiting (Recommended)
- Authentication endpoints: 5 requests per minute per IP
- General endpoints: 60 requests per minute per user
- Transfer endpoints: 10 requests per minute per user

### Security Headers (Recommended)
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy: default-src 'self'
