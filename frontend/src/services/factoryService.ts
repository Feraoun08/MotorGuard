import { api } from "./api";
import type { Factory, ProductionLine } from "../types/factory";

export const factoryService = {
  async getFactories(): Promise<Factory[]> {
    const response = await api.get<Factory[]>("/api/factories");
    return response.data;
  },

  async getFactory(factoryId: string): Promise<Factory> {
    const response = await api.get<Factory>(
      `/api/factories/${encodeURIComponent(factoryId)}`
    );

    return response.data;
  },

  async getProductionLines(factoryId: string): Promise<ProductionLine[]> {
    const response = await api.get<ProductionLine[]>(
      `/api/factories/${encodeURIComponent(factoryId)}/lines`
    );

    return response.data;
  },

  async getProductionLine(
    factoryId: string,
    lineId: string
  ): Promise<ProductionLine> {
    const response = await api.get<ProductionLine>(
      `/api/factories/${encodeURIComponent(factoryId)}/lines/${encodeURIComponent(lineId)}`
    );

    return response.data;
  },
};