import api from "./api"

export const authAPI = {
  // User Registration
  register: (data: { email: string; password: string; name: string; phone: string }) =>
    api.post("/auth/register/", data),

  // User Login
  login: (data: { email: string; password: string }) => api.post("/auth/login/", data),

  // Request OTP for login or operations
  requestOTP: (data: { email: string; type: "login" | "transfer" | "password-reset" }) =>
    api.post("/auth/otp/send", data),

  // Verify OTP code
  verifyOTP: (data: { email: string; otp: string; type: "login" | "transfer" | "password-reset" }) =>
    api.post("/auth/otp/verify", data),

  // Refresh Access Token
  refreshToken: (refreshToken: string) => api.post("/auth/refresh-token/", { refreshToken }),

  // Logout and blacklist token
  logout: () => api.post("/auth/logout/", {}),

  // Enable 2FA
  enableTwoFA: () => api.post("/users/2fa/enable/", {}),

  // Disable 2FA
  disableTwoFA: (data: { otp: string }) => api.post("/users/2fa/disable/", data),

  // Verify 2FA setup
  verifyTwoFA: (data: { otp: string }) => api.post("/auth/2fa/verify", data),
}
