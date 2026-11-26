import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      const detail = error.response.data?.detail;

      if (typeof detail === "string") {
        return detail;
      }

      if (Array.isArray(detail)) {
        return detail
          .map((item) => item.msg ?? "Validation error")
          .join(", ");
      }

      return `Request failed with status ${error.response.status}`;
    }

    if (error.request) {
      return "Unable to connect to the MotorGuard API.";
    }
  }

  return "An unexpected error occurred.";
}