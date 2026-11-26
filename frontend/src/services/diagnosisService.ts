import { api } from "./api";
import type { DiagnosisResponse } from "../types/diagnosis";

export const diagnosisService = {
  async diagnose(
    factoryId: string,
    motorId: string
  ): Promise<DiagnosisResponse> {
    const response = await api.get<DiagnosisResponse>(
      `/api/factories/${factoryId}/motors/${motorId}/diagnosis`
    );

    return response.data;
  },
};