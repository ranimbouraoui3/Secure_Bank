import api from "./api"

export const accountsAPI = {
  // Get all user accounts
  getAccounts: () => api.get("/accounts/"),

  // Get specific account details
  getAccountDetail: (accountId: string) => api.get(`/accounts/${accountId}/`),

  // Get account balance
  getAccountBalance: (accountId: string) => api.get(`/accounts/${accountId}/balance`),

  // Get account statement (transactions)
  getAccountStatement: (accountId: string, params?: { startDate?: string; endDate?: string; limit?: number }) =>
    api.get(`/accounts/${accountId}/statement`, { params }),

  // Update account nickname/details
  updateAccount: (accountId: string, data: { name: string }) => api.put(`/accounts/${accountId}`, data),
}
