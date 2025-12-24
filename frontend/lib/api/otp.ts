import api from "./api"

export const otpAPI = {
  // Send OTP to user email
  sendOTP: (data: { email: string; type: "login" | "transfer" | "password-reset" | "email-verification" }) =>
    api.post("/otp/send", data),

  // Verify OTP code
  verifyOTP: (data: {
    email: string
    otp: string
    type: "login" | "transfer" | "password-reset" | "email-verification"
  }) => api.post("/otp/verify", data),

  // Resend OTP (in case user didn't receive it)
  resendOTP: (data: { email: string; type: string }) => api.post("/otp/resend", data),

  // Get OTP status (for debugging)
  getOTPStatus: (email: string) => api.get(`/otp/status/${email}`),
}
