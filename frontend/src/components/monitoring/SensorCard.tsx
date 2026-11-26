import type { LucideIcon } from "lucide-react";

interface SensorCardProps {
  title: string;
  value: number | null | undefined;
  unit: string;
  icon: LucideIcon;
  description?: string;
  precision?: number;
}

export default function SensorCard({
  title,
  value,
  unit,
  icon: Icon,
  description,
  precision = 2,
}: SensorCardProps) {
  const valid = value !== null && value !== undefined && Number.isFinite(value);

  return (
    <div className="monitor-sensor-card">
      <div className="monitor-sensor-top">
        <span className="monitor-sensor-icon">
          <Icon size={19} />
        </span>

        <span className="monitor-sensor-title">{title}</span>
      </div>

      <div className="monitor-sensor-value">
        {valid ? value.toFixed(precision) : "--"}
        <span>{unit}</span>
      </div>

      {description && (
        <p className="monitor-sensor-description">{description}</p>
      )}
    </div>
  );
}