export interface ApiHealth {
  status?: string;
  [key: string]: unknown;
}

export interface ApiErrorDetail {
  loc?: Array<string | number>;
  msg: string;
  type?: string;
}

export interface ApiErrorResponse {
  detail?: string | ApiErrorDetail[];
}