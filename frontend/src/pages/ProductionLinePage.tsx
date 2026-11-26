import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowUpRight, Boxes } from "lucide-react";

import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";

import { factoryService } from "../services/factoryService";
import { motorService } from "../services/motorService";

import type { ProductionLine } from "../types/factory";
import type { Motor } from "../types/motor";

export default function ProductionLinePage() {
  const { factoryId = "", lineId = "" } = useParams();

  const [line, setLine] = useState<ProductionLine | null>(null);
  const [motors, setMotors] = useState<Motor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setLoading(true);
    setError(null);

    try {
      const [lineData, motorData] = await Promise.all([
        factoryService.getProductionLine(factoryId, lineId),
        motorService.getMotorsByLine(factoryId, lineId),
      ]);

      setLine(lineData);
      setMotors(motorData);
    } catch {
      setError("Unable to load production line data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, [factoryId, lineId]);

  if (loading) {
    return <LoadingState message="Loading production line..." />;
  }

  if (error || !line) {
    return (
      <ErrorState
        message={error ?? "Production line not found."}
        onRetry={loadData}
      />
    );
  }

  return (
    <div className="content-page">
      <Link
        to={`/factories/${encodeURIComponent(factoryId)}`}
        className="back-link"
      >
        <ArrowLeft size={15} />
        Back to factory
      </Link>

      <PageHeader
        eyebrow="PRODUCTION LINE"
        title={line.name}
        description={`Production line ID: ${line.id}`}
      />

      <div className="detail-banner">
        <div className="detail-banner-icon">
          <Boxes size={24} />
        </div>

        <div>
          <span className="detail-banner-label">REGISTERED ASSETS</span>
          <h2>{motors.length} motors</h2>
          <p>Motors associated with this production line.</p>
        </div>
      </div>

      <section className="factory-section">
        <div className="section-heading">
          <div>
            <h2>Motors</h2>
            <p>Explore the assets assigned to this production line.</p>
          </div>
        </div>

        {motors.length === 0 ? (
          <EmptyState
            title="No motors on this line"
            description="No motor assets were returned by the backend."
          />
        ) : (
          <div className="motor-grid">
            {motors.map((motor) => (
              <Link
                key={`${motor.factory_id}:${motor.id}`}
                to={`/factories/${encodeURIComponent(factoryId)}/motors/${encodeURIComponent(motor.id)}`}
                className="motor-card"
              >
                <div className="motor-card-icon">
                  <Boxes size={20} />
                </div>

                <div className="motor-card-content">
                  <h3>{motor.name}</h3>
                  <p>Motor ID · {motor.id}</p>
                  <span className="motor-card-link">
                    View asset <ArrowUpRight size={15} />
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}