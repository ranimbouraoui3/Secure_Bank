"use client"

import { CheckCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function SuccessAlert({ message, onDismiss }: { message: string; onDismiss?: () => void }) {
  return (
    <Alert className="mb-4 border-green-200 bg-green-50">
      <CheckCircle className="h-4 w-4 text-green-600" />
      <AlertDescription className="text-green-800">
        <div className="flex items-center justify-between">
          <span>{message}</span>
          {onDismiss && (
            <button onClick={onDismiss} className="ml-4 text-sm underline">
              Dismiss
            </button>
          )}
        </div>
      </AlertDescription>
    </Alert>
  )
}
