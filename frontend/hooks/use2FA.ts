"use client"

import { useState } from "react"
import { authAPI } from "@/lib/api"

export function use2FA() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [backupCodes, setBackupCodes] = useState<string[]>([])

  const enable2FA = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await authAPI.enableTwoFA()
      if (response.data.success) {
        setQrCode(response.data.qrCode || null)
        setBackupCodes(response.data.backupCodes || [])
        return response.data
      } else {
        throw new Error(response.data.error || "Failed to enable 2FA")
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || "Failed to enable 2FA"
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const disable2FA = async (otp: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await authAPI.disableTwoFA({ otp })
      if (response.data.success) {
        setQrCode(null)
        setBackupCodes([])
        return response.data
      } else {
        throw new Error(response.data.error || "Failed to disable 2FA")
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || "Failed to disable 2FA"
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const verify2FA = async (otp: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await authAPI.verifyTwoFA({ otp })
      if (response.data.success) {
        return response.data
      } else {
        throw new Error(response.data.error || "Invalid 2FA code")
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || "Failed to verify 2FA code"
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return {
    isLoading,
    error,
    qrCode,
    backupCodes,
    enable2FA,
    disable2FA,
    verify2FA,
  }
}
