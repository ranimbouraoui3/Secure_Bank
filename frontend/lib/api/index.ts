import api from "./api"
export { authAPI } from "./auth"
export { profileAPI } from "./profile"
export { accountsAPI } from "./accounts"
export { beneficiariesAPI } from "./beneficiaries"
export { transactionsAPI } from "./transactions"
export { otpAPI } from "./otp"
export { auditAPI } from "./audit"
export { securityAPI } from "./security"
export { api }

// API Error Response Interface
export interface APIErrorResponse {
  success: false
  error: string
  status: number
  details?: Record<string, any>
}

// API Success Response Interface
export interface APISuccessResponse<T> {
  success: true
  data: T
  message?: string
  timestamp?: string
}

// Centralized error handling utility
export const handleAPIError = (error: any): APIErrorResponse => {
  console.error("[API Error]", error)

  if (error.response) {
    // Server responded with error status
    return {
      success: false,
      error: error.response.data?.error || error.response.data?.message || "An error occurred",
      status: error.response.status,
      details: error.response.data?.details,
    }
  } else if (error.request) {
    // Request made but no response received
    return {
      success: false,
      error: "No response from server. Please check your connection.",
      status: 0,
    }
  } else {
    // Error setting up the request
    return {
      success: false,
      error: error.message || "An unexpected error occurred",
      status: 0,
    }
  }
}

// Utility to check if response is success
export const isSuccess = (response: any): response is APISuccessResponse<any> => {
  return response?.success === true
}

// Utility to check if response is error
export const isError = (response: any): response is APIErrorResponse => {
  return response?.success === false
}
