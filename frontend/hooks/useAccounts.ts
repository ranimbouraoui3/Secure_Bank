"use client"

import { useState, useEffect, useCallback } from "react"
import { accountsAPI, handleAPIError } from "@/lib/api"

export const useAccounts = () => {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAccounts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await accountsAPI.getAccounts()
      if (response.data.success) {
        setAccounts(response.data.accounts)
      }
    } catch (err) {
      const apiError = handleAPIError(err)
      setError(apiError.error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAccounts()
  }, [fetchAccounts])

  return { accounts, loading, error, refetch: fetchAccounts }
}
