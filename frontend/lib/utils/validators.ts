// lib/utils/validators.ts - Form validation utilities
export const validators = {
  email: (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  },

  password: (password: string) => {
    // Minimum 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special char
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
    return re.test(password)
  },

  phone: (phone: string) => {
    // Tunisian phone format
    const re = /^216[0-9]{8}$/
    return re.test(phone)
  },

  iban: (iban: string) => {
    // IBAN validation
    const re = /^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$/
    return re.test(iban)
  },

  amount: (amount: number) => {
    return amount > 0 && amount <= 1000000 && Number.isFinite(amount)
  },
}
