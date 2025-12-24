// hooks/useAuth.ts - Authentication hook
"use client"

import { useState, useCallback } from "react"
import { authAPI, handleAPIError } from "@/lib/api"

export const useAuth = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await authAPI.login({ email, password })
      if (response.data.success) {
        localStorage.setItem("token", response.data.token)
        localStorage.setItem("refreshToken", response.data.refreshToken)
        return response.data
      }
    } catch (err) {
      const apiError = handleAPIError(err)
      setError(apiError.error)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const register = useCallback(async (email: string, password: string, name: string, phone: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await authAPI.register({ email, password, name, phone })
      if (response.data.success) {
        return response.data
      }
    } catch (err) {
      const apiError = handleAPIError(err)
      setError(apiError.error)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem("refreshToken")
      if (refreshToken) {
        await authAPI.logout(refreshToken)
      }
      localStorage.removeItem("token")
      localStorage.removeItem("refreshToken")
    } catch (err) {
      console.error("Logout error:", err)
    }
  }, [])

  return { login, register, logout, loading, error }
}
