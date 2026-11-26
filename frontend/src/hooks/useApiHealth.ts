import { useCallback, useEffect, useState } from "react";
import { healthService } from "../services/healthService";

export type ApiStatus = "online" | "offline" | "checking";

export function useApiHealth(intervalMs = 15000) {
  const [status, setStatus] = useState<ApiStatus>("checking");
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const check = useCallback(async () => {
    try {
      await healthService.checkHealth();
      setStatus("online");
    } catch {
      setStatus("offline");
    } finally {
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    void check();

    const interval = window.setInterval(check, intervalMs);

    return () => window.clearInterval(interval);
  }, [check, intervalMs]);

  return {
    status,
    lastChecked,
    refresh: check,
  };
}