import {
  Factory,
  Boxes,
  Layers3,
} from "lucide-react";
import StatCard from "../common/StatCard";

interface DashboardOverviewProps {
  factoryCount: number;
  lineCount: number | null;
  motorCount: number | null;
}

export default function DashboardOverview({
  factoryCount,
  lineCount,
  motorCount,
}: DashboardOverviewProps) {
  return (
    <section className="stats-grid">
      <StatCard
        label="Factories"
        value={factoryCount}
        icon={<Factory size={19} />}
        description="Registered facilities"
      />

      <StatCard
        label="Production lines"
        value={lineCount ?? "—"}
        icon={<Layers3 size={19} />}
        description={
          lineCount === null
            ? "Data not yet available"
            : "Across registered factories"
        }
      />

      <StatCard
        label="Motors"
        value={motorCount ?? "—"}
        icon={<Boxes size={19} />}
        description={
          motorCount === null
            ? "Data not yet available"
            : "Registered motors"
        }
      />
    </section>
  );
}