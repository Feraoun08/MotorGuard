import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

import type { Telemetry } from "../../types/telemetry";

interface TelemetryChartProps {
  data: Telemetry[];
  title: string;
  dataKey: "temperature" | "current" | "rpm" | "rms";
  unit: string;
}

interface ChartPoint {
  timestamp: string;
  label: string;
  value: number;
}

function getChartData(
  telemetry: Telemetry[],
  dataKey: TelemetryChartProps["dataKey"]
): ChartPoint[] {
  return telemetry
    .filter((item) => item.timestamp)
    .map((item) => {
      let value: number | null = null;

      switch (dataKey) {
        case "temperature":
          value = item.sensors.temperature;
          break;

        case "current":
          value = item.sensors.current;
          break;

        case "rpm":
          value = item.sensors.rpm;
          break;

        case "rms":
          value = item.vibration.rms;
          break;
      }

      return {
        timestamp: item.timestamp,
        label: new Date(item.timestamp).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        value,
      };
    })
    .filter(
      (point): point is ChartPoint =>
        point.value !== null &&
        point.value !== undefined &&
        Number.isFinite(point.value)
    )
    .reverse();
}

export default function TelemetryChart({
  data,
  title,
  dataKey,
  unit,
}: TelemetryChartProps) {
  const chartData = getChartData(data, dataKey);

  return (
    <div className="telemetry-chart-card">
      <div className="telemetry-chart-header">
        <h3>{title}</h3>
        <span className="chart-unit">{unit}</span>
      </div>

      {chartData.length === 0 ? (
        <div className="chart-empty">
          No historical data available for this range.
        </div>
      ) : (
        <div className="telemetry-chart-container">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart
              data={chartData}
              margin={{ top: 10, right: 15, left: 0, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--border-color)"
              />

              <XAxis
                dataKey="label"
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                width={55}
              />

              <Tooltip
                formatter={(value) => [`${value} ${unit}`, title]}
                labelFormatter={(label) => `Time: ${label}`}
              />

              <Line
                type="monotone"
                dataKey="value"
                stroke="#2E8B57"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}