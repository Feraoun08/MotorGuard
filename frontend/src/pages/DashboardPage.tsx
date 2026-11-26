import { useEffect, useState } from "react";
import { ArrowUpRight, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";

import PageHeader from "../components/layout/PageHeader";
import DashboardOverview from "../components/dashboard/DashboardOverview";
import FactoryCard from "../components/dashboard/FactoryCard";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";

import { useFactories } from "../hooks/useFactories";
import { factoryService } from "../services/factoryService";
import { motorService } from "../services/motorService";

export default function DashboardPage() {
  const { factories, loading, error, refresh } = useFactories();

  const [lineCount, setLineCount] = useState<number | null>(null);
  const [motorCount, setMotorCount] = useState<number | null>(null);
  const [secondaryLoading, setSecondaryLoading] = useState(false);

  useEffect(() => {
    if (loading || error) return;

    let cancelled = false;

    async function loadCounts() {
      setSecondaryLoading(true);

      try {
        const lineResults = await Promise.all(
          factories.map((factory) =>
            factoryService.getProductionLines(factory.id)
          )
        );

        const totalLines = lineResults.reduce(
          (total, lines) => total + lines.length,
          0
        );

        const motors = await motorService.getMotors({
          limit: 1,
          offset: 0,
        });

        if (!cancelled) {
          setLineCount(totalLines);
          setMotorCount(motors.total);
        }
      } catch {
        if (!cancelled) {
          setLineCount(null);
          setMotorCount(null);
        }
      } finally {
        if (!cancelled) {
          setSecondaryLoading(false);
        }
      }
    }

    void loadCounts();

    return () => {
      cancelled = true;
    };
  }, [factories, loading, error]);

  if (loading) {
    return <LoadingState message="Loading MotorGuard overview..." />;
  }

  if (error) {
    return (
      <ErrorState
        message={error}
        onRetry={refresh}
      />
    );
  }

  return (
    <div className="dashboard-page">
      <section className="dashboard-hero">
        <div className="hero-orb hero-orb-one" />
        <div className="hero-orb hero-orb-two" />

        <div className="hero-content">
          <div className="hero-label">
            <span className="hero-label-dot" />
            INDUSTRIAL INTELLIGENCE PLATFORM
          </div>

          <h1>
            Monitoring made
            <br />
            <span>intelligent.</span>
          </h1>

          <p>
            A unified view of your industrial environment.
            Monitor your facilities, explore your assets
            and access predictive insights.
          </p>

          <Link to="/factories" className="hero-button">
            Explore facilities
            <ArrowUpRight size={17} />
          </Link>
        </div>

        <div className="hero-decoration">
          <div className="hero-decoration-circle">
            <div className="hero-decoration-inner">
              <span>MG</span>
              <div className="hero-decoration-line" />
              <small>MONITORING</small>
            </div>
          </div>
        </div>
      </section>

      <div className="dashboard-section">
        <PageHeader
          eyebrow="SYSTEM OVERVIEW"
          title="Your industrial environment"
          description="A summary of your registered infrastructure."
          action={
            <button
              className="button button-secondary"
              onClick={refresh}
            >
              <RefreshCw size={15} />
              Refresh
            </button>
          }
        />

        <DashboardOverview
          factoryCount={factories.length}
          lineCount={secondaryLoading ? null : lineCount}
          motorCount={secondaryLoading ? null : motorCount}
        />

        <section className="factory-section">
          <div className="section-heading">
            <div>
              <h2>Facilities</h2>
              <p>Explore factories and their production infrastructure.</p>
            </div>

            <Link to="/factories" className="text-link">
              All factories <ArrowUpRight size={16} />
            </Link>
          </div>

          {factories.length === 0 ? (
            <EmptyState
              title="No factories registered"
              description="Factories will appear here when they are available through the backend."
            />
          ) : (
            <div className="factory-grid">
              {factories.map((factory) => (
                <FactoryCard
                  key={factory.id}
                  factory={factory}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}