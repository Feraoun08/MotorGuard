import { api } from "./api";
import type {
  Telemetry,
  TelemetryHistoryResponse,
} from "../types/telemetry";

export const telemetryService = {
  async getLatest(
    factoryId: string,
    motorId: string
  ): Promise<Telemetry> {
    const response = await api.get<Telemetry>(
      `/api/factories/${factoryId}/motors/${motorId}/telemetry/latest`
    );

    return response.data;
  },

  async getHistory(
    factoryId: string,
    motorId: string,
    start: string,
    end: string,
    limit = 1000
  ): Promise<TelemetryHistoryResponse> {
    const response = await api.get<TelemetryHistoryResponse>(
      `/api/factories/${factoryId}/motors/${motorId}/telemetry`,
      {
        params: {
          start,
          end,
          limit,
        },
      }
    );

    return response.data;
  },
};