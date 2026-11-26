import { api } from "./api";
import type { Motor, MotorListResponse } from "../types/motor";

export const motorService = {
  async getMotorsByLine(
    factoryId: string,
    lineId: string
  ): Promise<Motor[]> {
    const response = await api.get<Motor[]>(
      `/api/factories/${encodeURIComponent(factoryId)}/lines/${encodeURIComponent(lineId)}/motors`
    );

    return response.data;
  },

  async getMotor(
    factoryId: string,
    motorId: string
  ): Promise<Motor> {
    const response = await api.get<Motor>(
      `/api/factories/${encodeURIComponent(factoryId)}/motors/${encodeURIComponent(motorId)}`
    );

    return response.data;
  },

  async getMotors(params?: {
    factory_id?: string;
    line_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<MotorListResponse> {
    const response = await api.get<MotorListResponse>("/api/motors", {
      params,
    });

    return response.data;
  },
};