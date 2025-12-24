import api from "./api"

export const beneficiariesAPI = {
  // Get all beneficiaries
  getBeneficiaries: () => api.get("/beneficiaries/"),

  // Get specific beneficiary details
  getBeneficiary: (beneficiaryId: string) => api.get(`/beneficiaries/${beneficiaryId}`),

  // Add new beneficiary
  addBeneficiary: (data: { name: string; iban: string; bankName: string }) => api.post("/beneficiaries/", data),

  // Update beneficiary information
  updateBeneficiary: (beneficiaryId: string, data: { name?: string; bankName?: string }) =>
    api.put(`/beneficiaries/${beneficiaryId}`, data),

  // Delete beneficiary
  deleteBeneficiary: (beneficiaryId: string) => api.delete(`/beneficiaries/${beneficiaryId}`),

  // Verify beneficiary (for some operations)
  verifyBeneficiary: (beneficiaryId: string) => api.post(`/beneficiaries/${beneficiaryId}/verify`, {}),
}
