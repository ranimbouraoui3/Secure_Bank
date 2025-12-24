# Complete API Endpoints Reference

This document lists all API endpoints implemented in the frontend to communicate with the Django REST backend.

## Authentication Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| POST | `/api/auth/register/` | Create user account | email, password, name, phone |
| POST | `/api/auth/login/` | User authentication with JWT | email, password |
| POST | `/api/auth/refresh-token/` | Refresh JWT token | refreshToken |
| POST | `/api/auth/logout/` | Secure user logout | - |
| POST | `/api/users/2fa/enable/` | Enable 2FA | - |
| POST | `/api/users/2fa/disable/` | Disable 2FA | otp |

## Account Management Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/accounts/` | List all bank accounts | - |
| GET | `/api/accounts/{account_id}/` | Get account details | account_id |

## Beneficiaries Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/beneficiaries/` | List authorized beneficiaries | - |
| POST | `/api/beneficiaries/` | Add new beneficiary | name, iban, bankName |

## Transfer Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| POST | `/api/transfers/initiate/` | Initiate bank transfer | fromAccountId, toBeneficiaryId/toIBAN, amount, description |
| POST | `/api/transfers/{transfer_id}/confirm-otp/` | Confirm transfer with OTP | transfer_id, otp |

## Transaction History Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/transactions/` | Get transaction history | accountId, type, status, dates, pagination |

## Security Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/security/login-events/` | View login events | limit, offset |
| GET | `/api/security/failed-attempts/` | View failed authentication attempts | limit, offset |
| POST | `/api/security/logout-all-devices/` | Logout from all active devices | - |

## Profile Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/users/profile/` | Get user profile | - |
| PATCH | `/api/users/profile/` | Update user profile | email, name, phone |
| POST | `/api/users/change-password/` | Change password | currentPassword, newPassword, confirmPassword |

## Implementation Notes

### Authentication Flow
1. User logs in via `/api/auth/login/`
2. Backend returns JWT access token and refresh token
3. Access token is stored in memory (React state)
4. Refresh token is stored in httpOnly cookie
5. Axios interceptor automatically adds Authorization header
6. On 401 error, attempt token refresh via `/api/auth/refresh-token/`

### Transfer Flow with OTP
1. Initiate transfer via `/api/transfers/initiate/`
2. Backend sends OTP to user email
3. User enters OTP in frontend
4. Confirm transfer via `/api/transfers/{transfer_id}/confirm-otp/`
5. Backend verifies OTP and executes transaction (ACID)
6. Confirmation email sent to user

### Security Features
- All endpoints require JWT authentication (except register/login)
- CORS protection enabled
- Rate limiting on authentication endpoints
- OTP verification for transfers
- Audit logging for all operations
- Session management with device tracking

## Usage Examples

### Login
\`\`\`typescript
import { authAPI } from '@/lib/api';

const response = await authAPI.login({
  email: 'user@example.com',
  password: 'SecurePass123!'
});
\`\`\`

### Initiate Transfer
\`\`\`typescript
import { transactionsAPI } from '@/lib/api';

const response = await transactionsAPI.initiateTransaction({
  fromAccountId: 'acc-123',
  toBeneficiaryId: 'ben-456',
  amount: 500.00,
  description: 'Payment'
});
\`\`\`

### Get Profile
\`\`\`typescript
import { profileAPI } from '@/lib/api';

const profile = await profileAPI.getProfile();
\`\`\`
