"use client"

import React from "react"

import { useState } from "react" // Import useEffect
import {
  CreditCard,
  ArrowLeft,
  Plus,
  Eye,
  EyeOff,
  LogOut,
  Lock,
  X,
  Send,
  Settings,
  Wallet,
  Shield,
  AlertCircle,
  DollarSign,
  Mail,
  Building,
  User,
  CheckCircle2,
  Clock,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface Account {
  id: string
  name: string
  balance: number
  iban: string
  accountType: "checking" | "savings"
}

interface Beneficiary {
  id: string
  name: string
  iban: string
  bankName: string
}

interface Transaction {
  id: string
  type: "sent" | "received"
  amount: number
  beneficiary: string
  date: string
  status: "completed" | "pending"
}

export default function BankingApp() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentPage, setCurrentPage] = useState("login")
  const [showBalance, setShowBalance] = useState(true)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [phone, setPhone] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [transferAmount, setTransferAmount] = useState("")
  const [selectedAccount, setSelectedAccount] = useState("")
  const [selectedBeneficiary, setSelectedBeneficiary] = useState("")
  const [beneficiaryName, setBeneficiaryName] = useState("")
  const [beneficiaryIBAN, setBeneficiaryIBAN] = useState("")
  const [beneficiaryBank, setBeneficiaryBank] = useState("")
  const [showAddBeneficiary, setShowAddBeneficiary] = useState(false)

  const [showTransferConfirm, setShowTransferConfirm] = useState(false)
  const [otp, setOtp] = useState("")
  const [otpTimer, setOtpTimer] = useState(300) // 5 minutes in seconds
  const [canResendOTP, setCanResendOTP] = useState(false)
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false)
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmNewPassword, setConfirmNewPassword] = useState("")
  const [profileEmail, setProfileEmail] = useState("")

  const [is2FAEnabled, setIs2FAEnabled] = useState(false)

  const [showAccountsList, setShowAccountsList] = useState(false)

  const [accounts] = useState<Account[]>([
    {
      id: "1",
      name: "Main Account",
      balance: 5250.75,
      iban: "TN5910006035183738981234",
      accountType: "checking",
    },
    {
      id: "2",
      name: "Savings Account",
      balance: 12450.0,
      iban: "TN5910006035183738981235",
      accountType: "savings",
    },
  ])

  const [beneficiaries] = useState<Beneficiary[]>([
    { id: "1", name: "Ahmed Ben Ali", iban: "TN5910006035183738981236", bankName: "STB" },
    { id: "2", name: "Fatima Khouja", iban: "TN5910006035183738981237", bankName: "BNA" },
  ])

  const [transactions] = useState<Transaction[]>([
    {
      id: "1",
      type: "sent",
      amount: 2000.0,
      beneficiary: "Fatima Khouja",
      date: "2025-12-14",
      status: "completed",
    },
    {
      id: "2",
      type: "received",
      amount: 500.0,
      beneficiary: "Fatima Khouja",
      date: "2024-01-14",
      status: "completed",
    },
    {
      id: "3",
      type: "sent",
      amount: 150.0,
      beneficiary: "Ahmed Ben Ali",
      date: "2024-01-13",
      status: "pending",
    },
  ])

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }
  const validatePhone = (phone: string) => {
    return /^\d{8}$/.test(phone)
  }
  const validatePassword = (pwd: string) => {
    return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(pwd)
  }

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")

    if (!email || !password) {
      setError("Please fill in all fields")
      return
    }

    if (!validateEmail(email)) {
      setError("Invalid email format")
      return
    }

    setIsLoggedIn(true)
    setSuccess("Login successful!")
    setCurrentPage("dashboard")
    setProfileEmail(email) // Store logged-in email for profile and OTP messages
    setPassword("") // Clear password after login
  }

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")

    if (!email || !password || !confirmPassword || !name || !phone) {
      setError("Please fill in all fields")
      return
    }

    if (!validateEmail(email)) {
      setError("Invalid email format")
      return
    }

    if (!validatePhone(phone)) {
      setError("Invalid phone number (8 digits required)")
      return
    }

    if (!validatePassword(password)) {
      setError("Password must be 8+ characters with uppercase, lowercase, digit, and special character")
      return
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }

    setSuccess("Registration successful! Please login.")
    setIsRegister(false)
    setEmail("")
    setPassword("")
    setConfirmPassword("")
    setName("")
    setPhone("")
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setCurrentPage("login")
    setEmail("")
    setPassword("")
    setError("")
    setSuccess("")
    setProfileEmail("") // Clear profile email on logout
  }

  React.useEffect(() => {
    if (showTransferConfirm && otpTimer > 0) {
      const interval = setInterval(() => {
        setOtpTimer((prev) => {
          if (prev <= 1) {
            setCanResendOTP(true)
            return 0
          }
          return prev - 1
        })
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [showTransferConfirm, otpTimer])

  const handleTransferConfirm = () => {
    if (!selectedAccount) {
      setError("Please select an account")
      return
    }
    if (!selectedBeneficiary) {
      setError("Please select a beneficiary")
      return
    }
    if (!transferAmount || Number.parseFloat(transferAmount) <= 0) {
      setError("Please enter a valid amount")
      return
    }
    if (Number.parseFloat(transferAmount) > 1000000) {
      setError("Amount cannot exceed 1,000,000 TND")
      return
    }

    setError("")
    setShowTransferConfirm(true)
    setOtp("")
    setOtpTimer(300)
    setCanResendOTP(false)
    // Simulate sending OTP
    setSuccess("OTP has been sent to your registered email")
    setTimeout(() => setSuccess(""), 3000)
  }

  const handleResendOTP = () => {
    setOtp("")
    setOtpTimer(300)
    setCanResendOTP(false)
    setSuccess("New OTP has been sent to your registered email")
    setTimeout(() => setSuccess(""), 3000)
  }

  const handleVerifyOTP = () => {
    if (!otp || otp.length !== 6) {
      setError("Please enter a valid 6-digit OTP")
      return
    }

    // Simulate OTP verification and transaction
    console.log("[v0] Processing transaction with OTP:", otp)

    // Call backend endpoint: POST /api/transactions/verify-and-execute
    // This would handle:
    // - OTP verification
    // - ACID transaction execution
    // - Email confirmation to profileEmail
    // - Audit logging

    setSuccess(`Transfer of ${transferAmount} TND completed successfully! Confirmation email sent to ${profileEmail}`)
    setTimeout(() => {
      setShowTransferConfirm(false)
      setCurrentPage("dashboard")
      setTransferAmount("")
      setSelectedAccount("")
      setSelectedBeneficiary("")
      setOtp("")
      setSuccess("") // Clear success message after a short delay
      setError("") // Clear any lingering errors
    }, 2000)
  }

  const handleChangePassword = () => {
    if (!currentPassword || !newPassword || !confirmNewPassword) {
      setError("Please fill in all password fields")
      return
    }

    if (!validatePassword(newPassword)) {
      setError("Password must be 8+ characters with uppercase, lowercase, digit, and special character")
      return
    }

    if (newPassword !== confirmNewPassword) {
      setError("New passwords do not match")
      return
    }

    setSuccess("Password changed successfully!")
    setCurrentPassword("")
    setNewPassword("")
    setConfirmNewPassword("")
    setShowChangePasswordModal(false)
    setError("") // Clear error after successful change
  }

  const handle2FAToggle = () => {
    setIs2FAEnabled(!is2FAEnabled)
    setSuccess(is2FAEnabled ? "2FA disabled successfully!" : "2FA enabled successfully!")
    setTimeout(() => setSuccess(""), 2000)
  }

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <CreditCard className="w-8 h-8 text-blue-600" />
            </div>
            <CardTitle>SecureBank</CardTitle>
            <CardDescription>{isRegister ? "Create your account" : "Sign in to your account"}</CardDescription>
          </CardHeader>

          <CardContent>
            {error && (
              <Alert className="mb-4 bg-red-50 border-red-200">
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}
            {success && (
              <Alert className="mb-4 bg-green-50 border-green-200">
                <AlertDescription className="text-green-800">{success}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={isRegister ? handleRegister : handleLogin} className="space-y-4">
              {isRegister && (
                <>
                  <div>
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="John Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="+216 98 123 456"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                </>
              )}

              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1"
                />
              </div>

              {isRegister && (
                <div>
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="mt-1"
                  />
                </div>
              )}

              <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700">
                {isRegister ? "Register" : "Sign In"}
              </Button>
            </form>

            <div className="mt-4 text-center text-sm">
              <button
                onClick={() => {
                  setIsRegister(!isRegister)
                  setError("")
                  setSuccess("")
                }}
                className="text-blue-600 hover:underline"
              >
                {isRegister ? "Already have an account? Sign in" : "Don't have an account? Register"}
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const renderDashboard = () => (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Welcome back</h1>
        <p className="text-gray-600">Manage your accounts and transactions</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {accounts.map((account) => (
          <Card key={account.id} className="overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
              <CardTitle className="text-lg">{account.name}</CardTitle>
              <CardDescription className="text-blue-100">{account.accountType}</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Available Balance</p>
                  <div className="flex items-center gap-2 mt-1">
                    <p className="text-2xl font-bold">{showBalance ? `${account.balance.toFixed(2)} TND` : "••••"}</p>
                    <button onClick={() => setShowBalance(!showBalance)} className="text-gray-600">
                      {showBalance ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-gray-600 break-all">{account.iban}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Button
          variant="outline"
          onClick={() => setCurrentPage("transfer")}
          className="flex flex-col items-center gap-2 h-auto py-4"
        >
          <Send className="w-5 h-5" />
          <span className="text-xs">Send Money</span>
        </Button>
        <Button
          variant="outline"
          onClick={() => setCurrentPage("beneficiaries")}
          className="flex flex-col items-center gap-2 h-auto py-4"
        >
          <Plus className="w-5 h-5" />
          <span className="text-xs">Beneficiaries</span>
        </Button>
        <Button
          variant="outline"
          onClick={() => setCurrentPage("transactions")}
          className="flex flex-col items-center gap-2 h-auto py-4"
        >
          <Wallet className="w-5 h-5" />
          <span className="text-xs">History</span>
        </Button>
        <Button
          variant="outline"
          onClick={() => setCurrentPage("profile")}
          className="flex flex-col items-center gap-2 h-auto py-4"
        >
          <Settings className="w-5 h-5" />
          <span className="text-xs">Profile</span>
        </Button>
      </div>

      <Button
        variant="outline"
        onClick={() => setShowAccountsList(true)}
        className="w-full flex items-center justify-center gap-2"
      >
        <CreditCard className="w-5 h-5" />
        View All Accounts
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {transactions.slice(0, 3).map((transaction) => (
              <div key={transaction.id} className="flex justify-between items-center pb-3 border-b last:border-0">
                <div>
                  <p className="font-medium">{transaction.beneficiary}</p>
                  <p className="text-sm text-gray-600">{transaction.date}</p>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${transaction.type === "sent" ? "text-red-600" : "text-green-600"}`}>
                    {transaction.type === "sent" ? "-" : "+"}
                    {transaction.amount.toFixed(2)} TND
                  </p>
                  <p className={`text-xs ${transaction.status === "completed" ? "text-green-600" : "text-yellow-600"}`}>
                    {transaction.status}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Accounts List Modal */}
      {showAccountsList && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-auto">
            <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white sticky top-0 z-10">
              <div className="flex justify-between items-center">
                <CardTitle>All Bank Accounts</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAccountsList(false)}
                  className="text-white hover:bg-white/20"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              {accounts.map((account) => (
                <div key={account.id} className="p-4 border rounded-lg hover:bg-gray-50 transition">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-lg">{account.name}</h3>
                      <p className="text-sm text-gray-600 capitalize">{account.accountType}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">{account.balance.toFixed(2)} TND</p>
                      <p className="text-xs text-gray-500">Available Balance</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <p className="text-xs text-gray-600">IBAN</p>
                    <p className="text-sm font-mono break-all">{account.iban}</p>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                      View Details
                    </Button>
                    <Button size="sm" className="flex-1 bg-blue-600 hover:bg-blue-700">
                      Transfer
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )

  const renderTransfer = () => (
    <div className="space-y-6">
      <Button
        variant="ghost"
        onClick={() => setCurrentPage("dashboard")}
        className="flex items-center gap-2 -ml-2 mb-4"
      >
        <ArrowLeft className="w-5 h-5" />
        Back
      </Button>

      <div>
        <h1 className="text-3xl font-bold">Send Money</h1>
        <p className="text-gray-600">Transfer funds to your beneficiaries</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <CardTitle className="text-lg">Select Account</CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-2">
              {accounts.map((account) => (
                <div
                  key={account.id}
                  onClick={() => setSelectedAccount(account.id)}
                  className={`p-3 border rounded-lg cursor-pointer transition ${
                    selectedAccount === account.id ? "bg-blue-100 border-blue-500" : "hover:bg-blue-50"
                  }`}
                >
                  <p className="font-medium">{account.name}</p>
                  <p className="text-sm text-gray-600">Balance: {account.balance.toFixed(2)} TND</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <CardTitle className="text-lg">Select Beneficiary</CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-2">
              {beneficiaries.map((beneficiary) => (
                <div
                  key={beneficiary.id}
                  onClick={() => setSelectedBeneficiary(beneficiary.id)}
                  className={`p-3 border rounded-lg cursor-pointer transition ${
                    selectedBeneficiary === beneficiary.id ? "bg-blue-100 border-blue-500" : "hover:bg-blue-50"
                  }`}
                >
                  <p className="font-medium">{beneficiary.name}</p>
                  <p className="text-sm text-gray-600">IBAN: {beneficiary.iban}</p>
                  <p className="text-sm text-gray-500">Bank: {beneficiary.bankName}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
          <CardTitle className="text-lg">Transfer Amount</CardTitle>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
          <div>
            <Label htmlFor="amount">Amount (TND)</Label>
            <Input
              id="amount"
              type="number"
              placeholder="0.00"
              value={transferAmount}
              onChange={(e) => {
                const val = e.target.value
                if (val === "" || /^\d*\.?\d{0,2}$/.test(val)) {
                  setTransferAmount(val)
                }
              }}
              className="mt-1"
              min="0"
              step="0.01"
              onBlur={() => {
                if (transferAmount && Number.parseFloat(transferAmount) > 0) {
                  console.log("[v0] Amount entered:", transferAmount)
                }
              }}
            />
            {transferAmount && Number.parseFloat(transferAmount) > 0 && (
              <p className="text-sm text-gray-600 mt-1">
                You will transfer: {Number.parseFloat(transferAmount).toFixed(2)} TND
              </p>
            )}
          </div>
          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-300 disabled:to-gray-400 transition-all shadow-md disabled:shadow-none"
            onClick={handleTransferConfirm}
            disabled={
              !selectedAccount || !selectedBeneficiary || !transferAmount || Number.parseFloat(transferAmount) <= 0
            }
          >
            {!selectedAccount || !selectedBeneficiary || !transferAmount || Number.parseFloat(transferAmount) <= 0
              ? "Complete All Fields to Continue"
              : "Continue to Confirm"}
          </Button>
        </CardContent>
      </Card>

      <Button variant="outline" onClick={() => setCurrentPage("dashboard")} className="w-full">
        Back
      </Button>

      {showTransferConfirm && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md shadow-2xl border-0 animate-in fade-in zoom-in duration-300">
            <CardHeader className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 text-white pb-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
              <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12"></div>
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                    <Shield className="w-6 h-6" />
                  </div>
                  <CardTitle className="text-2xl font-bold">Verify Transfer</CardTitle>
                </div>
                <p className="text-blue-100 text-sm">Please confirm your transaction with OTP</p>
              </div>
            </CardHeader>

            <CardContent className="pt-6 space-y-6">
              {/* Transaction Summary */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-blue-600" />
                  Transaction Details
                </h3>

                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 space-y-3 border border-blue-100">
                  <div className="flex justify-between items-center pb-3 border-b border-blue-200">
                    <span className="text-sm text-gray-600 flex items-center gap-2">
                      <Building className="w-4 h-4 text-gray-500" />
                      From Account
                    </span>
                    <span className="font-semibold text-gray-900">
                      {accounts.find((a) => a.id === selectedAccount)?.name}
                    </span>
                  </div>

                  <div className="flex justify-between items-center pb-3 border-b border-blue-200">
                    <span className="text-sm text-gray-600 flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-500" />
                      To Beneficiary
                    </span>
                    <span className="font-semibold text-gray-900">
                      {beneficiaries.find((b) => b.id === selectedBeneficiary)?.name}
                    </span>
                  </div>

                  <div className="flex justify-between items-center pt-2">
                    <span className="text-sm text-gray-600 flex items-center gap-2">
                      <DollarSign className="w-4 h-4 text-gray-500" />
                      Amount
                    </span>
                    <span className="text-2xl font-bold text-blue-700">
                      {Number.parseFloat(transferAmount).toFixed(2)} TND
                    </span>
                  </div>
                </div>
              </div>

              {/* OTP Input Section */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="otp" className="text-base font-semibold text-gray-700 flex items-center gap-2">
                    <Lock className="w-4 h-4" />
                    Enter Security Code
                  </Label>
                  <div className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full border border-green-200">
                    <Shield className="w-3 h-3" />
                    <span className="font-medium">Encrypted</span>
                  </div>
                </div>

                <div className="relative group">
                  <Input
                    id="otp"
                    type="text"
                    placeholder="● ● ● ● ● ●"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    maxLength={6}
                    className="text-center text-3xl tracking-[0.8em] font-mono font-bold border-2 border-blue-200 focus:border-blue-500 h-16 rounded-xl bg-white shadow-inner transition-all"
                    autoFocus
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2">
                    {otp.length === 6 ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    ) : (
                      <Lock className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                </div>

                {/* OTP Status Info */}
                <div className="flex items-center justify-between text-xs bg-gray-50 rounded-lg p-3 border">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Mail className="w-4 h-4" />
                    <span>Code sent to {profileEmail}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-blue-600" />
                    <span className="font-mono font-semibold text-blue-700">
                      {Math.floor(otpTimer / 60)}:{(otpTimer % 60).toString().padStart(2, "0")}
                    </span>
                  </div>
                </div>

                {/* Resend Button */}
                <button
                  onClick={handleResendOTP}
                  disabled={!canResendOTP}
                  className={`text-sm font-medium transition-all ${
                    canResendOTP
                      ? "text-blue-600 hover:text-blue-700 hover:underline cursor-pointer"
                      : "text-gray-400 cursor-not-allowed"
                  }`}
                >
                  {canResendOTP ? "Resend Code" : "Resend available after timer expires"}
                </button>
              </div>

              {error && (
                <Alert className="bg-red-50 border-red-200 border-l-4 border-l-red-500 animate-in slide-in-from-top">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  <AlertDescription className="text-red-800 font-medium">{error}</AlertDescription>
                </Alert>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1 h-12 border-2 hover:bg-gray-50 font-semibold transition-all bg-transparent"
                  onClick={() => {
                    setShowTransferConfirm(false)
                    setOtp("")
                    setError("")
                  }}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={handleVerifyOTP}
                  disabled={otp.length !== 6}
                >
                  {otp.length === 6 ? "Verify & Confirm" : "Enter OTP"}
                </Button>
              </div>

              {/* Security Notice */}
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <div className="text-xs text-amber-800 space-y-1">
                  <p className="font-semibold">Security Notice</p>
                  <p>Never share this OTP with anyone. Our staff will never ask for your OTP.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )

  const renderBeneficiaries = () => (
    <div className="space-y-6">
      <Button
        variant="ghost"
        onClick={() => setCurrentPage("dashboard")}
        className="flex items-center gap-2 -ml-2 mb-4"
      >
        <ArrowLeft className="w-5 h-5" />
        Back
      </Button>

      <div>
        <h1 className="text-3xl font-bold">Beneficiaries</h1>
        <p className="text-gray-600">Manage your trusted contacts</p>
      </div>

      {!showAddBeneficiary ? (
        <>
          <Button
            className="bg-blue-600 hover:bg-blue-700 w-full md:w-auto"
            onClick={() => setShowAddBeneficiary(true)}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Beneficiary
          </Button>

          <div className="grid gap-4">
            {beneficiaries.map((beneficiary) => (
              <Card key={beneficiary.id}>
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{beneficiary.name}</h3>
                      <p className="text-sm text-gray-600 break-all mt-1">IBAN: {beneficiary.iban}</p>
                      <p className="text-sm text-gray-500 mt-1">Bank: {beneficiary.bankName}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        Edit
                      </Button>
                      <Button size="sm" variant="destructive">
                        Delete
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      ) : (
        <Card className="overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <CardTitle>Add New Beneficiary</CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-4">
            <div>
              <Label htmlFor="bene-name">Beneficiary Name</Label>
              <Input
                id="bene-name"
                type="text"
                placeholder="John Doe"
                value={beneficiaryName}
                onChange={(e) => setBeneficiaryName(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="bene-iban">IBAN</Label>
              <Input
                id="bene-iban"
                type="text"
                placeholder="TN5910006104004095000000"
                value={beneficiaryIBAN}
                onChange={(e) => setBeneficiaryIBAN(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="bene-bank">Bank Name</Label>
              <Input
                id="bene-bank"
                type="text"
                placeholder="Bank Name"
                value={beneficiaryBank}
                onChange={(e) => setBeneficiaryBank(e.target.value)}
                className="mt-1"
              />
            </div>
            <div className="flex gap-2">
              <Button
                className="flex-1 bg-blue-600 hover:bg-blue-700"
                onClick={() => {
                  if (!beneficiaryName || !beneficiaryIBAN || !beneficiaryBank) {
                    setError("Please fill all fields")
                    return
                  }
                  setSuccess("Beneficiary added successfully!")
                  setTimeout(() => {
                    setBeneficiaryName("")
                    setBeneficiaryIBAN("")
                    setBeneficiaryBank("")
                    setShowAddBeneficiary(false)
                    setSuccess("")
                  }, 1500)
                }}
              >
                Add Beneficiary
              </Button>
              <Button
                variant="outline"
                className="flex-1 bg-transparent"
                onClick={() => {
                  setShowAddBeneficiary(false)
                  setBeneficiaryName("")
                  setBeneficiaryIBAN("")
                  setBeneficiaryBank("")
                }}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Button variant="outline" onClick={() => setCurrentPage("dashboard")} className="w-full">
        Back
      </Button>
    </div>
  )

  const renderTransactions = () => (
    <div className="space-y-6">
      <Button
        variant="ghost"
        onClick={() => setCurrentPage("dashboard")}
        className="flex items-center gap-2 -ml-2 mb-4"
      >
        <ArrowLeft className="w-5 h-5" />
        Back
      </Button>

      <div>
        <h1 className="text-3xl font-bold">Transaction History</h1>
        <p className="text-gray-600">View all your transactions</p>
      </div>

      <div className="flex gap-2 mb-4">
        <Button variant="outline" size="sm">
          All
        </Button>
        <Button variant="outline" size="sm">
          Sent
        </Button>
        <Button variant="outline" size="sm">
          Received
        </Button>
      </div>

      <div className="space-y-3">
        {transactions.map((transaction) => (
          <Card key={transaction.id}>
            <CardContent className="pt-6">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${transaction.type === "sent" ? "bg-red-100" : "bg-green-100"}`}>
                    <Wallet className={`w-5 h-5 ${transaction.type === "sent" ? "text-red-600" : "text-green-600"}`} />
                  </div>
                  <div>
                    <p className="font-medium">{transaction.beneficiary}</p>
                    <p className="text-sm text-gray-600">{transaction.date}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${transaction.type === "sent" ? "text-red-600" : "text-green-600"}`}>
                    {transaction.type === "sent" ? "-" : "+"}
                    {transaction.amount.toFixed(2)} TND
                  </p>
                  <p className={`text-xs ${transaction.status === "completed" ? "text-green-600" : "text-yellow-600"}`}>
                    {transaction.status}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Button variant="outline" onClick={() => setCurrentPage("dashboard")} className="w-full">
        Back
      </Button>
    </div>
  )

  const renderProfile = () => (
    <div className="space-y-6">
      <Button
        variant="ghost"
        onClick={() => setCurrentPage("dashboard")}
        className="flex items-center gap-2 -ml-2 mb-4"
      >
        <ArrowLeft className="w-5 h-5" />
        Back
      </Button>

      <div>
        <h1 className="text-3xl font-bold">Profile Settings</h1>
        <p className="text-gray-600">Manage your account information</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="email-profile">Email Address</Label>
            <Input
              id="email-profile"
              type="email"
              value={profileEmail}
              onChange={(e) => setProfileEmail(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="name-profile">Full Name</Label>
            <Input
              id="name-profile"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="phone-profile">Phone Number</Label>
            <Input
              id="phone-profile"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="mt-1"
            />
          </div>
          <Button className="w-full bg-blue-600 hover:bg-blue-700" onClick={() => setSuccess("Changes saved!")}>
            Save Changes
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <Shield className={`w-5 h-5 ${is2FAEnabled ? "text-green-600" : "text-gray-400"}`} />
              <div>
                <p className="font-medium">Two-Factor Authentication</p>
                <p className="text-sm text-gray-600">
                  {is2FAEnabled ? "2FA is currently enabled" : "Add an extra layer of security"}
                </p>
              </div>
            </div>
            <Button
              variant={is2FAEnabled ? "destructive" : "default"}
              size="sm"
              onClick={handle2FAToggle}
              className={is2FAEnabled ? "" : "bg-green-600 hover:bg-green-700"}
            >
              {is2FAEnabled ? "Disable" : "Enable"}
            </Button>
          </div>

          <div>
            <p className="text-sm text-gray-600">Last login: December 15, 2025 at 10:30 AM</p>
          </div>
          <Button variant="outline" className="w-full bg-transparent" onClick={() => setShowChangePasswordModal(true)}>
            <Lock className="w-4 h-4 mr-2" />
            Change Password
          </Button>
          <Button
            variant="outline"
            className="w-full bg-transparent"
            onClick={() => {
              setIsLoggedIn(false)
              setCurrentPage("login")
              setSuccess("Logged out successfully!")
            }}
          >
            Logout from all devices
          </Button>
        </CardContent>
      </Card>

      <Button
        variant="destructive"
        className="w-full"
        onClick={() => {
          setIsLoggedIn(false)
          setCurrentPage("login")
          setEmail("")
          setName("")
          setPhone("")
          setPassword("")
          setConfirmPassword("")
          setProfileEmail("") // Clear profile email on logout
        }}
      >
        <LogOut className="w-4 h-4 mr-2" />
        Sign Out
      </Button>

      <Button variant="outline" onClick={() => setCurrentPage("dashboard")} className="w-full">
        Back
      </Button>

      {showChangePasswordModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white flex justify-between items-center">
              <CardTitle>Change Password</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowChangePasswordModal(false)
                  setCurrentPassword("")
                  setNewPassword("")
                  setConfirmNewPassword("")
                  setError("") // Clear error when closing modal
                }}
                className="text-white hover:bg-white/20"
              >
                <X className="w-5 h-5" />
              </Button>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div>
                <Label htmlFor="current-pwd">Current Password</Label>
                <Input
                  id="current-pwd"
                  type="password"
                  placeholder="Enter current password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="new-pwd">New Password</Label>
                <Input
                  id="new-pwd"
                  type="password"
                  placeholder="Enter new password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="confirm-new-pwd">Confirm New Password</Label>
                <Input
                  id="confirm-new-pwd"
                  type="password"
                  placeholder="Confirm new password"
                  value={confirmNewPassword}
                  onChange={(e) => setConfirmNewPassword(e.target.value)}
                  className="mt-1"
                />
              </div>

              {error && (
                <Alert className="bg-red-50 border-red-200">
                  <AlertDescription className="text-red-800">{error}</AlertDescription>
                </Alert>
              )}

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1 bg-transparent"
                  onClick={() => {
                    setShowChangePasswordModal(false)
                    setCurrentPassword("")
                    setNewPassword("")
                    setConfirmNewPassword("")
                    setError("") // Clear error when closing modal
                  }}
                >
                  Cancel
                </Button>
                <Button className="flex-1 bg-blue-600 hover:bg-blue-700" onClick={handleChangePassword}>
                  Change Password
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <CreditCard className="w-6 h-6 text-blue-600" />
            <h1 className="text-xl font-bold">SecureBank</h1>
          </div>
          <Button variant="ghost" size="sm" onClick={handleLogout} className="flex items-center gap-2">
            <LogOut className="w-4 h-4" />
            Logout
          </Button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">{error}</div>}
        {success && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">{success}</div>
        )}

        {!isLoggedIn ? (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
              <CardHeader className="text-center">
                <div className="flex justify-center mb-4">
                  <CreditCard className="w-8 h-8 text-blue-600" />
                </div>
                <CardTitle>SecureBank</CardTitle>
                <CardDescription>{isRegister ? "Create your account" : "Sign in to your account"}</CardDescription>
              </CardHeader>

              <CardContent>
                {error && (
                  <Alert className="mb-4 bg-red-50 border-red-200">
                    <AlertDescription className="text-red-800">{error}</AlertDescription>
                  </Alert>
                )}
                {success && (
                  <Alert className="mb-4 bg-green-50 border-green-200">
                    <AlertDescription className="text-green-800">{success}</AlertDescription>
                  </Alert>
                )}

                <form onSubmit={isRegister ? handleRegister : handleLogin} className="space-y-4">
                  {isRegister && (
                    <>
                      <div>
                        <Label htmlFor="name">Full Name</Label>
                        <Input
                          id="name"
                          type="text"
                          placeholder="John Doe"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="phone">Phone Number</Label>
                        <Input
                          id="phone"
                          type="tel"
                          placeholder="+216 98 123 456"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          className="mt-1"
                        />
                      </div>
                    </>
                  )}

                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="mt-1"
                    />
                  </div>

                  {isRegister && (
                    <div>
                      <Label htmlFor="confirmPassword">Confirm Password</Label>
                      <Input
                        id="confirmPassword"
                        type="password"
                        placeholder="••••••••"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                  )}

                  <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700">
                    {isRegister ? "Register" : "Sign In"}
                  </Button>
                </form>

                <div className="mt-4 text-center text-sm">
                  <button
                    onClick={() => {
                      setIsRegister(!isRegister)
                      setError("")
                      setSuccess("")
                    }}
                    className="text-blue-600 hover:underline"
                  >
                    {isRegister ? "Already have an account? Sign in" : "Don't have an account? Register"}
                  </button>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <>
            {currentPage === "dashboard" && renderDashboard()}
            {currentPage === "transfer" && renderTransfer()}
            {currentPage === "beneficiaries" && renderBeneficiaries()}
            {currentPage === "transactions" && renderTransactions()}
            {currentPage === "profile" && renderProfile()}
          </>
        )}
      </main>
    </div>
  )
}
