/**
 * Reusable confirmation modal for delete operations and other confirmations.
 * Matches the design of LimitModal for consistency.
 */
import { useCallback, useEffect } from "react";
import { AlertTriangle, Trash2, X } from "lucide-react";

export type ConfirmationVariant = "destructive" | "warning";

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: ConfirmationVariant;
}

export function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "destructive",
}: ConfirmationModalProps) {
  // Handle Escape key
  const handleEscape = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  // Handle Enter key for confirmation
  const handleEnter = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        onConfirm();
      }
    },
    [onConfirm]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.addEventListener("keydown", handleEnter);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.removeEventListener("keydown", handleEnter);
      document.body.style.overflow = "";
    };
  }, [isOpen, handleEscape, handleEnter]);

  if (!isOpen) return null;

  const variantStyles = {
    destructive: {
      iconBg: "bg-red-100 dark:bg-red-900/30",
      iconColor: "text-red-600 dark:text-red-400",
      confirmBg:
        "bg-red-600 hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700",
      confirmText: "text-white",
      icon: Trash2,
    },
    warning: {
      iconBg: "bg-amber-100 dark:bg-amber-900/30",
      iconColor: "text-amber-600 dark:text-amber-400",
      confirmBg:
        "bg-amber-600 hover:bg-amber-700 dark:bg-amber-600 dark:hover:bg-amber-700",
      confirmText: "text-white",
      icon: AlertTriangle,
    },
  };

  const styles = variantStyles[variant];
  const Icon = styles.icon;

  return (
    <div className="fixed inset-0 z-[300] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md bg-white dark:bg-[#1a1a1a] rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg text-[#737373] hover:text-[#1a1a1a] dark:text-[#808080] dark:hover:text-white hover:bg-[#f0f0f0] dark:hover:bg-[#3a3a3a] transition-colors z-10"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Content */}
        <div className="p-8 pt-12">
          {/* Icon */}
          <div className="flex justify-center mb-4">
            <div
              className={`inline-flex items-center justify-center w-16 h-16 ${styles.iconBg} rounded-full`}
            >
              <Icon className={`w-8 h-8 ${styles.iconColor}`} />
            </div>
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold text-[#1a1a1a] dark:text-white text-center mb-3">
            {title}
          </h2>

          {/* Message */}
          <p className="text-[#737373] dark:text-[#a0a0a0] text-center mb-8">
            {message}
          </p>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-3 bg-[#f0f0f0] hover:bg-[#e0e0e0] dark:bg-[#2a2a2a] dark:hover:bg-[#3a3a3a] text-[#1a1a1a] dark:text-white rounded-xl font-medium transition-colors"
            >
              {cancelText}
            </button>
            <button
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className={`flex-1 px-4 py-3 ${styles.confirmBg} ${styles.confirmText} rounded-xl font-medium transition-colors`}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
