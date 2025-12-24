// lib/utils/format.ts - Formatting utilities
export const formatCurrency = (amount: number, currency = "TND") => {
  return new Intl.NumberFormat("fr-TN", {
    style: "currency",
    currency,
  }).format(amount)
}

export const formatDate = (date: string | Date) => {
  return new Intl.DateTimeFormat("fr-TN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(date))
}

export const formatIBAN = (iban: string) => {
  return iban.replace(/(.{4})/g, "$1 ").trim()
}

export const truncateEmail = (email: string) => {
  const [username, domain] = email.split("@")
  if (username.length <= 3) return email
  return `${username.substring(0, 3)}***@${domain}`
}
