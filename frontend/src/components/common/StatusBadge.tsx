interface StatusBadgeProps {
  label: string;
  variant?: "success" | "warning" | "danger" | "neutral";
}

export default function StatusBadge({
  label,
  variant = "neutral",
}: StatusBadgeProps) {
  return (
    <span className={`status-badge status-${variant}`}>
      <span className="status-dot" />
      {label}
    </span>
  );
}