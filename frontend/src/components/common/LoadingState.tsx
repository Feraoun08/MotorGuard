import { LoaderCircle } from "lucide-react";

interface LoadingStateProps {
  message?: string;
}

export default function LoadingState({
  message = "Loading data...",
}: LoadingStateProps) {
  return (
    <div className="state-container">
      <LoaderCircle className="loading-icon" size={24} />
      <p>{message}</p>
    </div>
  );
}