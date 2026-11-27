
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
import ChartEmptyState from "./ChartEmptyState";

interface TelemetryChartProps {
  data: Telemetry[];
  title: string;
  dataKey: "temperature" | "current" | "rpm" | "rms";
  unit: string;
}

interface ChartPoint {
  timestamp: string;
  value: number;
}

function getChartData(
  telemetry: Telemetry[],
  dataKey: TelemetryChartProps["dataKey"]
): ChartPoint[] {
  const points = telemetry
    .map((item) => {
      let value: number | null | undefined;

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

      const timestamp = item.timestamp;

      if (
        !timestamp ||
        value === null ||
        value === undefined ||
        !Number.isFinite(value) ||
        Number.isNaN(new Date(timestamp).getTime())
      ) {
        return null;
      }

      return {
        timestamp,
        value,
      };
    })
    .filter((point): point is ChartPoint => point !== null);

  // Chronological order.
  return points.sort(
    (a, b) =>
      new Date(a.timestamp).getTime() -
      new Date(b.timestamp).getTime()
  );
}

function formatAxisTime(timestamp: string) {
  const date = new Date(timestamp);

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatTooltipTime(timestamp: string) {
  return new Date(timestamp).toLocaleString();
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
        <span className="chart-unit">{unit || "No unit"}</span>
      </div>

      {chartData.length === 0 ? (
        <ChartEmptyState message="No historical data available for this range." />
      ) : (
        <div className="telemetry-chart-container">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart
              data={chartData}
              margin={{ top: 12, right: 15, left: 0, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--border-color)"
              />

              <XAxis
                dataKey="timestamp"
                tickFormatter={formatAxisTime}
                minTickGap={35}
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                width={55}
                domain={["auto", "auto"]}
              />

              <Tooltip
                contentStyle={{
                  background: "var(--surface)",
                  border: "1px solid var(--border-color)",
                  borderRadius: "10px",
                  fontSize: "12px",
                }}
                labelFormatter={(label) =>
                  `Time: ${formatTooltipTime(String(label))}`
                }
                formatter={(value) => [
                  `${Number(value).toLocaleString(undefined, {
                    maximumFractionDigits: 4,
                  })}${unit ? ` ${unit}` : ""}`,
                  title,
                ]}
              />

              <Line
                type="monotone"
                dataKey="value"
                name={title}
                stroke="#2E8B57"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5 }}
                connectNulls={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
