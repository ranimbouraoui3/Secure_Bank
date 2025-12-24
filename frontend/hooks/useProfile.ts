"use client"

import { useState, useCallback } from "react"
import { profileAPI, handleAPIError } from "@/lib/api"

export const useProfile = () => {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchProfile = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await profileAPI.getProfile()
      if (response.data.success) {
        setProfile(response.data.user)
      }
    } catch (err) {
      const apiError = handleAPIError(err)
      setError(apiError.error)
    } finally {
      setLoading(false)
    }
  }, [])

  const updateProfile = useCallback(async (data: any) => {
    setLoading(true)
    setError(null)
    try {
      const response = await profileAPI.updateProfile(data)
      if (response.data.success) {
        setProfile(response.data.user)
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

  const changePassword = useCallback(async (data: any) => {
    setLoading(true)
    setError(null)
    try {
      const response = await profileAPI.changePassword(data)
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

  return { profile, loading, error, fetchProfile, updateProfile, changePassword }
}
