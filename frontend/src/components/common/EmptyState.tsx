import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description?: string;
}

export default function EmptyState({
  title,
  description,
}: EmptyStateProps) {
  return (
    <div className="state-container">
      <Inbox size={28} />

      <h3>{title}</h3>

      {description && <p>{description}</p>}
    </div>
  );
}