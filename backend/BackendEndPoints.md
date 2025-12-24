# Banking App API Endpoints

## 1️⃣ Authentication Endpoints

| URL                  | Method | Description                      |
| -------------------- | ------ | -------------------------------- |
| `/api/auth/register` | POST   | Register a new user              |
| `/api/auth/login`    | POST   | Login user and get JWT tokens    |
| `/api/auth/logout`   | POST   | Logout user / invalidate session |
| `/api/auth/refresh`  | POST   | Refresh JWT token                |

## 2️⃣ Profile Endpoints

| URL                            | Method      | Description              |
| ------------------------------ | ----------- | ------------------------ |
| `/api/profile`                 | GET         | Get current user profile |
| `/api/profile/update`          | PUT / PATCH | Update profile info      |
| `/api/profile/change-password` | POST        | Change password          |

## 3️⃣ OTP Endpoints

| URL               | Method | Description      |
| ----------------- | ------ | ---------------- |
| `/api/otp/send`   | POST   | Send OTP to user |
| `/api/otp/verify` | POST   | Verify OTP code  |

## 4️⃣ Accounts Endpoints

| URL                               | Method | Description                       |
| --------------------------------- | ------ | --------------------------------- |
| `/api/accounts`                   | GET    | Get list of user accounts         |
| `/api/accounts/<uuid:account_id>` | GET    | Get details of a specific account |

## 5️⃣ Beneficiaries Endpoints

| URL                                               | Method      | Description             |
| ------------------------------------------------- | ----------- | ----------------------- |
| `/api/beneficiaries`                              | GET         | List all beneficiaries  |
| `/api/beneficiaries/add`                          | POST        | Add a new beneficiary   |
| `/api/beneficiaries/<uuid:beneficiary_id>`        | DELETE      | Delete a beneficiary    |
| `/api/beneficiaries/<uuid:beneficiary_id>/update` | PUT / PATCH | Update beneficiary info |

## 6️⃣ Transactions Endpoints

| URL                                       | Method | Description                            |
| ----------------------------------------- | ------ | -------------------------------------- |
| `/api/transactions`                       | GET    | List all transactions for user         |
| `/api/transactions/<uuid:transaction_id>` | GET    | Get details of a transaction           |
| `/api/transactions/initiate`              | POST   | Initiate a new transaction (OTP sent)  |
| `/api/transactions/verify-and-execute`    | POST   | Verify OTP and execute the transaction |

## 7️⃣ Audit Logs Endpoints

| URL               | Method | Description                        |
| ----------------- | ------ | ---------------------------------- |
| `/api/audit/logs` | GET    | Get audit logs of actions performe |
