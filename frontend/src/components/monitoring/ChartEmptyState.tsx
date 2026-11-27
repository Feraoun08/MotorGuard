
import { Activity } from "lucide-react";

interface ChartEmptyStateProps {
  message?: string;
}

export default function ChartEmptyState({
  message = "No telemetry data available for this period.",
}: ChartEmptyStateProps) {
  return (
    <div className="chart-empty-state">
      <div className="chart-empty-icon">
        <Activity size={26} />
      </div>

      <p>{message}</p>

      <span>
        Historical measurements will appear when telemetry becomes available.
      </span>
    </div>
  );
}
