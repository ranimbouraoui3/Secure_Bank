// components/transfers/TransferForm.tsx - Transfer form component
"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { accountsAPI, beneficiariesAPI, transactionsAPI, handleAPIError } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"

const TransferForm = () => {
  const [step, setStep] = useState(1)
  const [accounts, setAccounts] = useState<any[]>([])
  const [beneficiaries, setBeneficiaries] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [formData, setFormData] = useState({
    fromAccountId: "",
    toBeneficiaryId: "",
    amount: "",
    description: "",
  })

  const [otpData, setOtpData] = useState({
    transactionId: "",
    otp: "",
  })

  useEffect(() => {
    loadAccountsAndBeneficiaries()
  }, [])

  const loadAccountsAndBeneficiaries = async () => {
    try {
      setLoading(true)
      const [accountsRes, beneficiariesRes] = await Promise.all([
        accountsAPI.getAccounts(),
        beneficiariesAPI.getBeneficiaries(),
      ])

      if (accountsRes.data.success) setAccounts(accountsRes.data.accounts)
      if (beneficiariesRes.data.success) setBeneficiaries(beneficiariesRes.data.beneficiaries)
    } catch (err) {
      const errorData = handleAPIError(err)
      setError(errorData.error)
    } finally {
      setLoading(false)
    }
  }

  const handleInitiateTransfer = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    if (!formData.fromAccountId || !formData.toBeneficiaryId || !formData.amount) {
      setError("Please fill in all required fields")
      setLoading(false)
      return
    }

    try {
      const response = await transactionsAPI.initiateTransaction(formData)
      if (response.data.success) {
        setOtpData((prev) => ({ ...prev, transactionId: response.data.transactionId }))
        setStep(2)
        setSuccess("OTP sent to your email")
      }
    } catch (err) {
      const errorData = handleAPIError(err)
      setError(errorData.error)
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyAndExecute = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const response = await transactionsAPI.verifyAndExecute(otpData)
      if (response.data.success) {
        setSuccess("Transfer completed successfully!")
        setTimeout(() => {
          setStep(1)
          setFormData({ fromAccountId: "", toBeneficiaryId: "", amount: "", description: "" })
        }, 3000)
      }
    } catch (err) {
      const errorData = handleAPIError(err)
      setError(errorData.error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6 max-w-2xl">
      <h2 className="text-2xl font-bold mb-6">{step === 1 ? "New Transfer" : "Verify Transfer"}</h2>

      {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700">{error}</div>}
      {success && <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded text-green-700">{success}</div>}

      {step === 1 && (
        <form onSubmit={handleInitiateTransfer} className="space-y-4">
          <div>
            <Label>From Account</Label>
            <Select
              value={formData.fromAccountId}
              onValueChange={(value) => setFormData({ ...formData, fromAccountId: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select account" />
              </SelectTrigger>
              <SelectContent>
                {accounts.map((account) => (
                  <SelectItem key={account.id} value={account.id}>
                    {account.name} - {account.balance.toFixed(2)} {account.currency}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>To Beneficiary</Label>
            <Select
              value={formData.toBeneficiaryId}
              onValueChange={(value) => setFormData({ ...formData, toBeneficiaryId: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select beneficiary" />
              </SelectTrigger>
              <SelectContent>
                {beneficiaries.map((b) => (
                  <SelectItem key={b.id} value={b.id}>
                    {b.name} - {b.iban}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="amount">Amount (TND)</Label>
            <Input
              id="amount"
              type="number"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              step="0.01"
              min="0.01"
              placeholder="0.00"
            />
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Payment description..."
              rows={3}
            />
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Processing..." : "Continue to OTP"}
          </Button>
        </form>
      )}

      {step === 2 && (
        <form onSubmit={handleVerifyAndExecute} className="space-y-4">
          <div className="bg-blue-50 p-4 rounded border border-blue-200">
            <p className="text-sm text-blue-800">OTP sent to your email. Enter the 6-digit code.</p>
          </div>

          <div>
            <Label htmlFor="otp">OTP Code</Label>
            <Input
              id="otp"
              type="text"
              value={otpData.otp}
              onChange={(e) => setOtpData({ ...otpData, otp: e.target.value })}
              maxLength={6}
              placeholder="000000"
              className="text-center text-2xl tracking-widest"
            />
          </div>

          <div className="flex gap-4">
            <Button type="button" variant="outline" onClick={() => setStep(1)} className="flex-1">
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? "Verifying..." : "Complete"}
            </Button>
          </div>
        </form>
      )}
    </Card>
  )
}

export default TransferForm
