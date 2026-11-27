
import { useState } from "react";
import {
  Activity,
  Thermometer,
  Gauge,
  Zap,
  Clock,
  RefreshCw,
  ArrowLeft,
} from "lucide-react";

import { Link, useParams } from "react-router-dom";

import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import Breadcrumbs from "../components/common/Breadcrumbs";

import SensorCard from "../components/monitoring/SensorCard";
import VibrationGrid from "../components/monitoring/VibrationGrid";
import TelemetryChart from "../components/monitoring/TelemetryChart";
import DiagnosisCard from "../components/monitoring/DiagnosisCard";

import { useMotorMonitoring } from "../hooks/useMotorMonitoring";

import type { TelemetryRange } from "../types/telemetry";

const ranges: { value: TelemetryRange; label: string }[] = [
  { value: "1h", label: "1 hour" },
  { value: "6h", label: "6 hours" },
  { value: "24h", label: "24 hours" },
  { value: "7d", label: "7 days" },
];

export default function MotorMonitoringPage() {
  const { factoryId, motorId } = useParams<{
    factoryId: string;
    motorId: string;
  }>();

  const [range, setRange] = useState<TelemetryRange>("1h");

  const safeFactoryId = factoryId ?? "";
  const safeMotorId = motorId ?? "";

  const {
    motor,
    latest,
    history,
    diagnosis,

    loading,
    refreshing,

    error,
    diagnosisError,

    refresh,
    refreshDiagnosis,
  } = useMotorMonitoring(
    safeFactoryId,
    safeMotorId,
    range
  );

  if (!factoryId || !motorId) {
    return (
      <ErrorState
        title="Invalid motor route"
        message="The factory or motor identifier is missing."
      />
    );
  }

  if (loading && !latest) {
    return <LoadingState message="Loading motor monitoring..." />;
  }

  if (error && !latest) {
    return (
      <ErrorState
        title="Monitoring unavailable"
        message={error}
        onRetry={refresh}
      />
    );
  }

  if (!latest) {
    return (
      <ErrorState
        title="No telemetry available"
        message="This motor has no telemetry data available yet."
        onRetry={refresh}
      />
    );
  }

  const sensors = latest.sensors;
  const vibration = latest.vibration;

  return (
    <div className="motor-monitoring-page">
      <Breadcrumbs
        items={[
          {
            label: "Factories",
            path: "/factories",
          },
          {
            label: factoryId,
            path: `/factories/${encodeURIComponent(factoryId)}`,
          },
          {
            label: motor?.name ?? motorId,
          },
        ]}
      />

      <div className="monitoring-back">
        <Link to={`/factories/${encodeURIComponent(factoryId)}`}>
          <ArrowLeft size={16} />
          Back to factory
        </Link>
      </div>

      <PageHeader
        eyebrow="Equipment monitoring"
        title={motor?.name ?? motorId}
        description={`Live monitoring for motor ${motorId}`}
      />

      {error && (
        <div className="monitoring-warning" role="status">
          {error}
        </div>
      )}

      {/* Motor identity and status */}
      <section className="motor-monitor-identity">
        <div className="motor-monitor-identity-main">
          <div className="motor-monitor-avatar">
            <Activity size={28} />
          </div>

          <div>
            <div className="motor-monitor-name">
              {motor?.name ?? motorId}
            </div>

            <div className="motor-monitor-id">
              {motorId}
            </div>
          </div>
        </div>

        <div className="monitor-motor-context">
          <span>Factory: {factoryId}</span>

          {motor?.line_id && (
            <span>Line: {motor.line_id}</span>
          )}
        </div>

        <div className="motor-monitor-badges">
          <span className="monitor-badge">
            State: {latest.motor_state || "Unknown"}
          </span>

          <span className="monitor-badge">
            Bearing: {latest.bearing_condition || "Unknown"}
          </span>

          {latest.is_simulated && (
            <span className="monitor-badge simulated">
              Simulated telemetry
            </span>
          )}
        </div>

        <div className="monitor-last-update">
          <Clock size={14} />

          <span>
            Last telemetry:{" "}
            {new Date(latest.timestamp).toLocaleString()}
          </span>

          {refreshing && (
            <RefreshCw size={14} className="spin" />
          )}
        </div>
      </section>

      {/* Sensor KPI cards */}
      <section className="monitor-section">
        <div className="monitor-section-heading">
          <div>
            <h2>Sensor measurements</h2>
            <p>Latest available telemetry</p>
          </div>
        </div>

        <div className="monitor-sensor-grid">
          <SensorCard
            title="Temperature"
            value={sensors.temperature}
            unit="°C"
            icon={Thermometer}
            precision={2}
          />

          <SensorCard
            title="Current"
            value={sensors.current}
            unit="A"
            icon={Zap}
            precision={3}
          />

          <SensorCard
            title="Speed"
            value={sensors.rpm}
            unit="RPM"
            icon={Gauge}
            precision={0}
          />

          <SensorCard
            title="Vibration RMS"
            value={vibration.rms}
            unit=""
            icon={Activity}
            precision={4}
          />
        </div>
      </section>

      {/* Vibration features */}
      <section className="monitor-section">
        <div className="monitor-section-heading">
          <div>
            <h2>Vibration analysis</h2>
            <p>
              Statistical features extracted from the vibration signal
            </p>
          </div>
        </div>

        <VibrationGrid vibration={vibration} />
      </section>

      {/* Historical charts */}
      <section className="monitor-section">
        <div className="monitor-section-heading chart-section-heading">
          <div>
            <h2>Historical telemetry</h2>
            <p>Explore sensor evolution over time</p>
          </div>

          <div
            className="range-selector"
            role="group"
            aria-label="Historical telemetry time range"
          >
            {ranges.map((item) => (
              <button
                key={item.value}
                type="button"
                className={range === item.value ? "active" : ""}
                aria-pressed={range === item.value}
                onClick={() => setRange(item.value)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="monitor-charts-grid">
          <TelemetryChart
            data={history}
            title="Temperature"
            dataKey="temperature"
            unit="°C"
          />

          <TelemetryChart
            data={history}
            title="Current"
            dataKey="current"
            unit="A"
          />

          <TelemetryChart
            data={history}
            title="Rotational speed"
            dataKey="rpm"
            unit="RPM"
          />

          <TelemetryChart
            data={history}
            title="Vibration RMS"
            dataKey="rms"
            unit=""
          />
        </div>
      </section>

      {/* ML Diagnosis */}
      <section className="monitor-section">
        <div className="monitor-section-heading">
          <div>
            <h2>Predictive maintenance</h2>
            <p>Model-based motor condition classification</p>
          </div>
        </div>

        <DiagnosisCard
          diagnosis={diagnosis}
          error={diagnosisError}
          onRefresh={refreshDiagnosis}
        />
      </section>

      {/* Footer controls */}
      <div className="monitor-footer-actions">
        <button
          type="button"
          className="monitor-refresh-button"
          onClick={() => {
            void refresh();
            void refreshDiagnosis();
          }}
          disabled={refreshing}
        >
          <RefreshCw
            size={16}
            className={refreshing ? "spin" : ""}
          />
          {refreshing ? "Refreshing..." : "Refresh monitoring"}
        </button>
      </div>
    </div>
  );
}
