
import { useCallback, useEffect, useRef, useState } from "react";

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
const POLLING_INTERVAL = 5000;

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

function createInitialState(): MonitoringState {
  return {
    motor: null,
    latest: null,
    history: [],
    diagnosis: null,

    loading: true,
    refreshing: false,

    error: null,
    diagnosisError: null,
  };
}

export function useMotorMonitoring(
  factoryId: string,
  motorId: string,
  range: TelemetryRange
) {
  const [state, setState] = useState<MonitoringState>(
    createInitialState
  );

  const contextKey = `${factoryId}:${motorId}:${range}`;

  const activeContextRef = useRef(contextKey);
  const monitoringRequestRef = useRef<string | null>(null);
  const diagnosisRequestRef = useRef(0);
  const mountedRef = useRef(false);

  // Keep the active context current, even before effects run.
  activeContextRef.current = contextKey;

  const loadMonitoring = useCallback(
    async (initial = false) => {
      const requestKey = contextKey;

      // Avoid overlapping requests for the same context.
      if (monitoringRequestRef.current === requestKey) {
        return;
      }

      monitoringRequestRef.current = requestKey;

      setState((previous) => ({
        ...previous,
        loading: initial && !previous.latest,
        refreshing: !initial,
        error: null,
      }));

      try {
        const dates = getRangeDates(range);

        const [motorResult, latestResult, historyResult] =
          await Promise.allSettled([
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

        // Ignore responses from a motor/range that is no longer active.
        if (
          !mountedRef.current ||
          activeContextRef.current !== requestKey
        ) {
          return;
        }

        const motorFailed = motorResult.status === "rejected";
        const latestFailed = latestResult.status === "rejected";
        const historyFailed = historyResult.status === "rejected";

        setState((previous) => ({
          ...previous,

          motor:
            motorResult.status === "fulfilled"
              ? motorResult.value
              : previous.motor,

          latest:
            latestResult.status === "fulfilled"
              ? latestResult.value
              : previous.latest,

          history:
            historyResult.status === "fulfilled"
              ? historyResult.value.items
              : previous.history,

          loading: false,
          refreshing: false,

          error:
            motorFailed && latestFailed && historyFailed
              ? "Unable to retrieve monitoring data. Previously available data is retained."
              : latestFailed
                ? "Latest telemetry could not be refreshed. Showing previously available measurements."
                : historyFailed
                  ? "Historical telemetry could not be refreshed. Showing previously available history."
                  : motorFailed
                    ? "Motor information could not be refreshed. Previously available information is retained."
                    : null,
        }));
      } catch (error) {
        console.error("Monitoring data loading failed:", error);

        if (
          mountedRef.current &&
          activeContextRef.current === requestKey
        ) {
          setState((previous) => ({
            ...previous,
            loading: false,
            refreshing: false,
            error: "Unable to refresh monitoring data.",
          }));
        }
      } finally {
        if (monitoringRequestRef.current === requestKey) {
          monitoringRequestRef.current = null;
        }
      }
    },
    [factoryId, motorId, range, contextKey]
  );

  const refreshDiagnosis = useCallback(async () => {
    const requestKey = contextKey;
    const requestId = ++diagnosisRequestRef.current;

    setState((previous) => ({
      ...previous,
      diagnosisError: null,
    }));

    try {
      const diagnosis = await diagnosisService.diagnose(
        factoryId,
        motorId
      );

      if (
        !mountedRef.current ||
        activeContextRef.current !== requestKey ||
        requestId !== diagnosisRequestRef.current
      ) {
        return;
      }

      setState((previous) => ({
        ...previous,
        diagnosis,
        diagnosisError: null,
      }));
    } catch (error) {
      console.error("ML diagnosis failed:", error);

      if (
        mountedRef.current &&
        activeContextRef.current === requestKey &&
        requestId === diagnosisRequestRef.current
      ) {
        setState((previous) => ({
          ...previous,
          diagnosisError:
            "Unable to obtain a new ML diagnosis. Previously available diagnosis is retained.",
        }));
      }
    }
  }, [factoryId, motorId, contextKey]);

  // Track the current mounted instance.
  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
      diagnosisRequestRef.current += 1;
    };
  }, []);

  // Reset data when navigating to a different motor or range.
  useEffect(() => {
    setState(createInitialState());

    void loadMonitoring(true);
    void refreshDiagnosis();

    const interval = window.setInterval(() => {
      void loadMonitoring(false);
    }, POLLING_INTERVAL);

    return () => {
      window.clearInterval(interval);
    };
  }, [loadMonitoring, refreshDiagnosis]);

  const refresh = useCallback(() => {
    return loadMonitoring(false);
  }, [loadMonitoring]);

  return {
    ...state,
    refresh,
    refreshDiagnosis,
  };
}
