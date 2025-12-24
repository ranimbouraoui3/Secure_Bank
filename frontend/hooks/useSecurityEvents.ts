"use client"

import { useState } from "react"
import { securityAPI } from "@/lib/api"
import type { LoginEvent, FailedAttempt, PaginationParams } from "@/lib/types/api-types"

export function useSecurityEvents() {
  const [loginEvents, setLoginEvents] = useState<LoginEvent[]>([])
  const [failedAttempts, setFailedAttempts] = useState<FailedAttempt[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchLoginEvents = async (params?: PaginationParams) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await securityAPI.getLoginEvents(params)
      if (response.data.success) {
        setLoginEvents(response.data.loginEvents || [])
      }
    } catch (err: any) {
      setError(err.response?.data?.error || "Failed to fetch login events")
    } finally {
      setIsLoading(false)
    }
  }

  const fetchFailedAttempts = async (params?: PaginationParams) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await securityAPI.getFailedAttempts(params)
      if (response.data.success) {
        setFailedAttempts(response.data.failedAttempts || [])
      }
    } catch (err: any) {
      setError(err.response?.data?.error || "Failed to fetch failed attempts")
    } finally {
      setIsLoading(false)
    }
  }

  const logoutAllDevices = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await securityAPI.logoutAllDevices()
      return response.data
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || "Failed to logout from all devices"
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return {
    loginEvents,
    failedAttempts,
    isLoading,
    error,
    fetchLoginEvents,
    fetchFailedAttempts,
    logoutAllDevices,
  }
}
