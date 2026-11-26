
import { useCallback, useEffect, useState } from "react";
import { factoryService } from "../services/factoryService";
import type { Factory, ProductionLine } from "../types/factory";

export function useFactories() {
  const [factories, setFactories] = useState<Factory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await factoryService.getFactories();
      setFactories(data);
    } catch {
      setError("Failed to load factories.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    factories,
    loading,
    error,
    refresh,
  };
}

export function useFactoryDetails(factoryId: string) {
  const [factory, setFactory] = useState<Factory | null>(null);
  const [lines, setLines] = useState<ProductionLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!factoryId) return;

    setLoading(true);
    setError(null);

    try {
      const [factoryData, lineData] = await Promise.all([
        factoryService.getFactory(factoryId),
        factoryService.getProductionLines(factoryId),
      ]);

      setFactory(factoryData);
      setLines(lineData);
    } catch {
      setError("Failed to load factory information.");
    } finally {
      setLoading(false);
    }
  }, [factoryId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    factory,
    lines,
    loading,
    error,
    refresh,
  };
}