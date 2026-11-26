export interface VibrationFeatures {
  max: number;
  min: number;
  mean: number;
  sd: number;
  rms: number;
  skewness: number;
  kurtosis: number;
  crest: number;
  form: number;
}

export interface MotorSensors {
  temperature: number | null;
  current: number | null;
  rpm: number | null;
}

export interface Telemetry {
  factory_id: string;
  motor_id: string;
  timestamp: string;

  motor_state: string;
  bearing_condition: string;

  ground_truth: string | null;
  is_simulated: boolean;

  vibration: VibrationFeatures;
  sensors: MotorSensors;

  additional_tags?: Record<string, unknown>;
}

export interface TelemetryHistoryResponse {
  factory_id: string;
  motor_id: string;
  start: string;
  end: string;
  count: number;
  limit: number;
  items: Telemetry[];
}

export type TelemetryRange = "1h" | "6h" | "24h" | "7d";