"use client"

import { useState, useEffect, useCallback } from "react"
import { transactionsAPI, handleAPIError } from "@/lib/api"

export const useTransactions = () => {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTransactions = useCallback(async (params?: any) => {
    setLoading(true)
    setError(null)
    try {
      const response = await transactionsAPI.getTransactions(params)
      if (response.data.success) {
        setTransactions(response.data.transactions)
      }
    } catch (err) {
      const apiError = handleAPIError(err)
      setError(apiError.error)
    } finally {
      setLoading(false)
    }
  }, [])

  const initiateTransaction = useCallback(async (data: any) => {
    setLoading(true)
    setError(null)
    try {
      const response = await transactionsAPI.initiateTransaction(data)
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

  const verifyAndExecute = useCallback(
    async (data: any) => {
      setLoading(true)
      setError(null)
      try {
        const response = await transactionsAPI.verifyAndExecute(data)
        if (response.data.success) {
          setTransactions([response.data.transaction, ...transactions])
          return response.data
        }
      } catch (err) {
        const apiError = handleAPIError(err)
        setError(apiError.error)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [transactions],
  )

  useEffect(() => {
    fetchTransactions()
  }, [fetchTransactions])

  return { transactions, loading, error, initiateTransaction, verifyAndExecute, refetch: fetchTransactions }
}
