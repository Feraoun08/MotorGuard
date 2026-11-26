export interface Motor {
  factory_id: string;
  id: string;
  line_id: string;
  name: string;
  created_at: string;
}

export interface MotorListResponse {
  items: Motor[];
  total: number;
  limit: number;
  offset: number;
}