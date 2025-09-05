import * as React from "react"
import { cn } from "../../lib/utils"

interface ToastProps {
  message: string
  type?: 'success' | 'error' | 'info'
  onClose: () => void
}

export function Toast({ message, type = 'info', onClose }: ToastProps) {
  React.useEffect(() => {
    const timer = setTimeout(onClose, 5000)
    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <div className={cn(
      "fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm",
      type === 'success' && "bg-green-100 text-green-800 border border-green-200",
      type === 'error' && "bg-red-100 text-red-800 border border-red-200",
      type === 'info' && "bg-blue-100 text-blue-800 border border-blue-200"
    )}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">{message}</p>
        <button
          onClick={onClose}
          className="ml-2 text-gray-400 hover:text-gray-600"
        >
          ×
        </button>
      </div>
    </div>
  )
}