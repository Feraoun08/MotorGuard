import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowUpRight, Layers3 } from "lucide-react";

import { useFactoryDetails } from "../hooks/useFactories";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";

export default function FactoryDetailsPage() {
  const { factoryId = "" } = useParams();

  const {
    factory,
    lines,
    loading,
    error,
    refresh,
  } = useFactoryDetails(factoryId);

  if (loading) {
    return <LoadingState message="Loading factory..." />;
  }

  if (error || !factory) {
    return (
      <ErrorState
        message={error ?? "Factory not found."}
        onRetry={refresh}
      />
    );
  }

  return (
    <div className="content-page">
      <Link to="/factories" className="back-link">
        <ArrowLeft size={15} />
        All factories
      </Link>

      <PageHeader
        eyebrow="FACILITY DETAILS"
        title={factory.name}
        description={`Factory identifier: ${factory.id}`}
      />

      <section className="detail-banner">
        <div className="detail-banner-icon">
          <Layers3 size={24} />
        </div>

        <div>
          <span className="detail-banner-label">PRODUCTION INFRASTRUCTURE</span>
          <h2>{lines.length} production lines</h2>
          <p>Registered production lines associated with this facility.</p>
        </div>
      </section>

      <section className="factory-section">
        <div className="section-heading">
          <div>
            <h2>Production lines</h2>
            <p>Choose a line to view its connected motors.</p>
          </div>
        </div>

        {lines.length === 0 ? (
          <EmptyState
            title="No production lines"
            description="This factory has no production lines registered in the API."
          />
        ) : (
          <div className="line-grid">
            {lines.map((line) => (
              <Link
                key={line.id}
                to={`/factories/${encodeURIComponent(factoryId)}/lines/${encodeURIComponent(line.id)}`}
                className="line-card"
              >
                <div className="line-card-icon">
                  <Layers3 size={20} />
                </div>

                <div className="line-card-content">
                  <h3>{line.name}</h3>
                  <p>Line ID · {line.id}</p>
                  <span className="line-card-link">
                    View line <ArrowUpRight size={15} />
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