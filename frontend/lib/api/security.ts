import api from "./api"

export const securityAPI = {
  // Get login events history
  getLoginEvents: (params?: { limit?: number; offset?: number }) => api.get("/security/login-events", { params }),

  // Get failed authentication attempts
  getFailedAttempts: (params?: { limit?: number; offset?: number }) => api.get("/security/failed-attempts", { params }),

  // Logout from all devices
  logoutAllDevices: () => api.post("/security/logout-all-devices", {}),
}
