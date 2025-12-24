import api from "./api"

export const transactionsAPI = {
  // Get all transactions with filters
  getTransactions: (params?: {
    accountId?: string
    type?: "sent" | "received"
    status?: "completed" | "pending" | "failed"
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }) => api.get("/transactions/", { params }),

  // Get transaction details
  getTransactionDetail: (transactionId: string) => api.get(`/transactions/${transactionId}`),

  // Initiate a new transfer
  initiateTransaction: (data: {
    fromAccountId: string
    toBeneficiaryId?: string
    toIBAN?: string
    amount: number
    description?: string
  }) => api.post("/transfers/initiate/", data),

  // Verify OTP and confirm transfer
  verifyAndExecute: (transferId: string, data: { otp: string }) =>
    api.post(`/transfers/${transferId}/confirm-otp/`, data),

  // Get pending transaction details
  getPendingTransaction: (transactionId: string) => api.get(`/transactions/${transactionId}/pending`),

  // Cancel pending transaction
  cancelTransaction: (transactionId: string) => api.post(`/transactions/${transactionId}/cancel`, {}),

  // Retry failed transaction
  retryTransaction: (transactionId: string) => api.post(`/transactions/${transactionId}/retry`, {}),

  // Export transactions as CSV/PDF
  exportTransactions: (format: "csv" | "pdf", params?: { startDate?: string; endDate?: string }) =>
    api.get("/transactions/export", { params: { ...params, format }, responseType: "blob" }),
}
