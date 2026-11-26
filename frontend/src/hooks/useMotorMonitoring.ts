import { useCallback, useEffect, useState } from "react";

import { telemetryService } from "../services/telemetryService";
import { diagnosisService } from "../services/diagnosisService";
import { motorService } from "../services/motorService";

import type { Motor } from "../types/motor";
import type { Telemetry, TelemetryRange } from "../types/telemetry";
import type { DiagnosisResponse } from "../types/diagnosis";

const RANGE_DURATION_MS: Record<TelemetryRange, number> = {
  "1h": 60 * 60 * 1000,
  "6h": 6 * 60 * 60 * 1000,
  "24h": 24 * 60 * 60 * 1000,
  "7d": 7 * 24 * 60 * 60 * 1000,
};

const HISTORY_LIMIT = 1000;

interface MonitoringState {
  motor: Motor | null;
  latest: Telemetry | null;
  history: Telemetry[];
  diagnosis: DiagnosisResponse | null;

  loading: boolean;
  refreshing: boolean;

  error: string | null;
  diagnosisError: string | null;
}

function getRangeDates(range: TelemetryRange) {
  const end = new Date();
  const start = new Date(end.getTime() - RANGE_DURATION_MS[range]);

  return {
    start: start.toISOString(),
    end: end.toISOString(),
  };
}

export function useMotorMonitoring(
  factoryId: string,
  motorId: string,
  range: TelemetryRange
) {
  const [state, setState] = useState<MonitoringState>({
    motor: null,
    latest: null,
    history: [],
    diagnosis: null,

    loading: true,
    refreshing: false,

    error: null,
    diagnosisError: null,
  });

  const loadMonitoring = useCallback(
    async (initial = false) => {
      if (initial) {
        setState((previous) => ({
          ...previous,
          loading: true,
          error: null,
        }));
      } else {
        setState((previous) => ({
          ...previous,
          refreshing: true,
          error: null,
        }));
      }

      try {
        const dates = getRangeDates(range);

        const [motor, latest, history] = await Promise.all([
          motorService.getMotor(factoryId, motorId),

          telemetryService.getLatest(factoryId, motorId),

          telemetryService.getHistory(
            factoryId,
            motorId,
            dates.start,
            dates.end,
            HISTORY_LIMIT
          ),
        ]);

        setState((previous) => ({
          ...previous,
          motor,
          latest,
          history: history.items,
          loading: false,
          refreshing: false,
          error: null,
        }));
      } catch (error) {
        console.error("Monitoring data loading failed:", error);

        setState((previous) => ({
          ...previous,
          loading: false,
          refreshing: false,
          error: "Unable to load motor monitoring data.",
        }));
      }
    },
    [factoryId, motorId, range]
  );

  const refreshDiagnosis = useCallback(async () => {
    try {
      setState((previous) => ({
        ...previous,
        diagnosisError: null,
      }));

      const diagnosis = await diagnosisService.diagnose(
        factoryId,
        motorId
      );

      setState((previous) => ({
        ...previous,
        diagnosis,
        diagnosisError: null,
      }));
    } catch (error) {
      console.error("ML diagnosis failed:", error);

      setState((previous) => ({
        ...previous,
        diagnosisError: "Unable to obtain ML diagnosis.",
      }));
    }
  }, [factoryId, motorId]);

  useEffect(() => {
    loadMonitoring(true);
  }, [loadMonitoring]);

  useEffect(() => {
    const interval = window.setInterval(() => {
      loadMonitoring(false);
    }, 5000);

    return () => window.clearInterval(interval);
  }, [loadMonitoring]);

  useEffect(() => {
    refreshDiagnosis();
  }, [refreshDiagnosis]);

  return {
    ...state,
    refresh: () => loadMonitoring(false),
    refreshDiagnosis,
  };
}