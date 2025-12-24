import api from "./api"

export const auditAPI = {
  // Get audit logs with filters
  getAuditLogs: (params?: {
    userId?: string
    action?: string
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }) => api.get("/audit/logs", { params }),

  // Get audit log by ID
  getAuditLog: (logId: string) => api.get(`/audit/logs/${logId}`),

  // Get user activity summary
  getActivitySummary: () => api.get("/audit/activity-summary"),

  // Get security events
  getSecurityEvents: (params?: { limit?: number; offset?: number }) => api.get("/audit/security-events", { params }),

  // Export audit logs
  exportAuditLogs: (format: "csv" | "pdf", params?: { startDate?: string; endDate?: string }) =>
    api.get("/audit/export", { params: { ...params, format }, responseType: "blob" }),
}
