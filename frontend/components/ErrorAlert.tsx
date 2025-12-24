"use client"

import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function ErrorAlert({ error, onDismiss }: { error: string; onDismiss?: () => void }) {
  return (
    <Alert variant="destructive" className="mb-4">
      <AlertCircle className="h-4 w-4" />
      <AlertDescription>
        <div className="flex items-center justify-between">
          <span>{error}</span>
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
