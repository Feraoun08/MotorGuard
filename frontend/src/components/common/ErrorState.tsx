import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="error-state">
      <div className="error-state-icon">
        <AlertCircle size={24} />
      </div>

      <div className="error-state-content">
        <h3>{title}</h3>
        <p>{message}</p>

        {onRetry && (
          <button
            className="error-state-retry"
            onClick={onRetry}
          >
            <RefreshCw size={15} />
            Try again
          </button>
        )}
      </div>
    </div>
  );
}