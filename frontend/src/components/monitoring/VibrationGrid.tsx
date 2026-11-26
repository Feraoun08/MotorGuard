import type { VibrationFeatures } from "../../types/telemetry";

interface VibrationGridProps {
  vibration: VibrationFeatures;
}

const featureInfo: {
  key: keyof VibrationFeatures;
  label: string;
  description: string;
}[] = [
  {
    key: "max",
    label: "Maximum",
    description: "Maximum vibration amplitude",
  },
  {
    key: "min",
    label: "Minimum",
    description: "Minimum vibration amplitude",
  },
  {
    key: "mean",
    label: "Mean",
    description: "Average signal value",
  },
  {
    key: "sd",
    label: "Standard Deviation",
    description: "Signal dispersion",
  },
  {
    key: "rms",
    label: "RMS",
    description: "Root mean square",
  },
  {
    key: "skewness",
    label: "Skewness",
    description: "Signal asymmetry",
  },
  {
    key: "kurtosis",
    label: "Kurtosis",
    description: "Signal distribution shape",
  },
  {
    key: "crest",
    label: "Crest Factor",
    description: "Peak-to-RMS ratio",
  },
  {
    key: "form",
    label: "Form Factor",
    description: "RMS-to-average ratio",
  },
];

export default function VibrationGrid({
  vibration,
}: VibrationGridProps) {
  return (
    <div className="vibration-grid">
      {featureInfo.map((feature) => {
        const value = vibration[feature.key];

        return (
          <div className="vibration-feature-card" key={feature.key}>
            <span className="vibration-feature-label">
              {feature.label}
            </span>

            <strong className="vibration-feature-value">
              {Number.isFinite(value) ? value.toFixed(4) : "--"}
            </strong>

            <span className="vibration-feature-description">
              {feature.description}
            </span>
          </div>
        );
      })}
    </div>
  );
}