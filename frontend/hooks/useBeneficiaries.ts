"use client"

import { useState, useEffect, useCallback } from "react"
import { beneficiariesAPI, handleAPIError } from "@/lib/api"

export const useBeneficiaries = () => {
  const [beneficiaries, setBeneficiaries] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchBeneficiaries = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await beneficiariesAPI.getBeneficiaries()
      if (response.data.success) {
        setBeneficiaries(response.data.beneficiaries)
      }
    } catch (err) {
      const apiError = handleAPIError(err)
      setError(apiError.error)
    } finally {
      setLoading(false)
    }
  }, [])

  const addBeneficiary = useCallback(
    async (data: any) => {
      setLoading(true)
      setError(null)
      try {
        const response = await beneficiariesAPI.addBeneficiary(data)
        if (response.data.success) {
          setBeneficiaries([...beneficiaries, response.data.beneficiary])
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
    [beneficiaries],
  )

  const deleteBeneficiary = useCallback(
    async (beneficiaryId: string) => {
      setLoading(true)
      setError(null)
      try {
        const response = await beneficiariesAPI.deleteBeneficiary(beneficiaryId)
        if (response.data.success) {
          setBeneficiaries(beneficiaries.filter((b) => b.id !== beneficiaryId))
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
    [beneficiaries],
  )

  useEffect(() => {
    fetchBeneficiaries()
  }, [fetchBeneficiaries])

  return { beneficiaries, loading, error, addBeneficiary, deleteBeneficiary, refetch: fetchBeneficiaries }
}
