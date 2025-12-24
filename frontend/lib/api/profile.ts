import api from "./api"

export const profileAPI = {
  // Get user profile
  getProfile: () => api.get("/users/profile/"),

  // Update profile information
  updateProfile: (data: { email?: string; name?: string; phone?: string }) => api.patch("/users/profile/", data),

  // Change password
  changePassword: (data: { currentPassword: string; newPassword: string; confirmPassword: string }) =>
    api.post("/users/change-password/", data),

  // Request email verification
  requestEmailVerification: () => api.post("/profile/email/verify-request", {}),

  // Verify email with OTP
  verifyEmail: (data: { otp: string }) => api.post("/profile/email/verify", data),

  // Update phone number
  updatePhoneNumber: (data: { phone: string }) => api.put("/profile/phone", data),

  // Get last login info
  getLastLogin: () => api.get("/profile/last-login"),

  // Get account settings
  getSettings: () => api.get("/profile/settings"),

  // Update account settings
  updateSettings: (data: { notificationsEmail?: boolean; notificationsSMS?: boolean }) =>
    api.put("/profile/settings", data),

  // Delete account
  deleteAccount: (data: { password: string }) => api.post("/profile/delete", data),
}
