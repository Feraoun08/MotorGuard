export interface Factory {
  id: string;
  name: string;
  created_at: string;
}

export interface ProductionLine {
  factory_id: string;
  id: string;
  name: string;
}