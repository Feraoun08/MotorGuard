export interface DiagnosisResponse {
  factory_id: string;
  motor_id: string;
  timestamp: string;

  predicted_class: string;
  confidence: number;

  ground_truth?: string | null;
  is_simulated?: boolean;
}