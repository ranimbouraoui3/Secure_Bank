"use client"

import { useState } from "react"
import { transactionsAPI, otpAPI } from "@/lib/api"
import type { InitiateTransferRequest, InitiateTransferResponse, ConfirmTransferResponse } from "@/lib/types/api-types"

export function useTransfer() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [transferId, setTransferId] = useState<string | null>(null)
  const [requiresOTP, setRequiresOTP] = useState(false)

  // Step 1: Initiate transfer
  const initiateTransfer = async (data: InitiateTransferRequest): Promise<InitiateTransferResponse> => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await transactionsAPI.initiateTransaction(data)

      if (response.data.success) {
        setTransferId(response.data.transferId)
        setRequiresOTP(response.data.requiresOTP)
        return response.data
      } else {
        throw new Error(response.data.error || "Failed to initiate transfer")
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || "Failed to initiate transfer"
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  // Step 2: Confirm transfer with OTP
  const confirmTransfer = async (otp: string): Promise<ConfirmTransferResponse> => {
    if (!transferId) {
      throw new Error("No transfer ID found. Please initiate a transfer first.")
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await transactionsAPI.verifyAndExecute(transferId, { otp })

      if (response.data.success) {
        // Reset state after successful transfer
        setTransferId(null)
        setRequiresOTP(false)
        return response.data
      } else {
        throw new Error(response.data.error || "Failed to confirm transfer")
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || "Invalid OTP or transfer failed"
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  // Resend OTP if needed
  const resendOTP = async (email: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await otpAPI.resendOTP({ email, type: "transfer" })
      return response.data
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || "Failed to resend OTP"
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  // Reset state
  const resetTransfer = () => {
    setTransferId(null)
    setRequiresOTP(false)
    setError(null)
  }

  return {
    isLoading,
    error,
    transferId,
    requiresOTP,
    initiateTransfer,
    confirmTransfer,
    resendOTP,
    resetTransfer,
  }
}
