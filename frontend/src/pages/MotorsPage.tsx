import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight, Boxes } from "lucide-react";

import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";

import { motorService } from "../services/motorService";
import type { Motor } from "../types/motor";

export default function MotorsPage() {
  const [motors, setMotors] = useState<Motor[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadMotors() {
    setLoading(true);
    setError(null);

    try {
      const response = await motorService.getMotors({
        limit: 100,
        offset: 0,
      });

      setMotors(response.items);
      setTotal(response.total);
    } catch {
      setError("Unable to load motor assets.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadMotors();
  }, []);

  if (loading) {
    return <LoadingState message="Loading motor assets..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={loadMotors} />;
  }

  return (
    <div className="content-page">
      <PageHeader
        eyebrow="ASSET DIRECTORY"
        title="Motors"
        description="Browse motor assets registered across your industrial facilities."
      />

      <div className="list-summary">
        <span>{total} motors registered</span>
        <span>Showing {motors.length} assets</span>
      </div>

      {motors.length === 0 ? (
        <EmptyState
          title="No motors registered"
          description="Motor assets will appear here once they are available through the API."
        />
      ) : (
        <div className="motor-grid">
          {motors.map((motor) => (
            <Link
              key={`${motor.factory_id}:${motor.id}`}
              to={`/factories/${encodeURIComponent(motor.factory_id)}/motors/${encodeURIComponent(motor.id)}`}
              className="motor-card"
            >
              <div className="motor-card-icon">
                <Boxes size={20} />
              </div>

              <div className="motor-card-content">
                <h3>{motor.name}</h3>
                <p>Motor ID · {motor.id}</p>
                <p>Factory · {motor.factory_id}</p>
                <p>Production line · {motor.line_id}</p>

                <span className="motor-card-link">
                  View asset <ArrowUpRight size={15} />
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}