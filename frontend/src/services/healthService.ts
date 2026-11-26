import { api } from "./api";
import type { ApiHealth } from "../types/api";

export const healthService = {
  async checkHealth(): Promise<ApiHealth> {
    const response = await api.get<ApiHealth>("/api/health");
    return response.data;
  },

  async checkReadiness(): Promise<ApiHealth> {
    const response = await api.get<ApiHealth>("/api/health/ready");
    return response.data;
  },
};