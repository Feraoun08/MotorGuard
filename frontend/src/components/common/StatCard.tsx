import type { ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  description?: string;
}

export default function StatCard({
  label,
  value,
  icon,
  description,
}: StatCardProps) {
  return (
    <article className="stat-card">
      <div className="stat-card-top">
        <span className="stat-card-label">{label}</span>
        <div className="stat-card-icon">{icon}</div>
      </div>

      <div className="stat-card-value">{value}</div>

      {description && (
        <div className="stat-card-description">{description}</div>
      )}
    </article>
  );
}