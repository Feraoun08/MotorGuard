import { useFactories } from "../hooks/useFactories";
import PageHeader from "../components/layout/PageHeader";
import FactoryCard from "../components/dashboard/FactoryCard";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";

export default function FactoriesPage() {
  const { factories, loading, error, refresh } = useFactories();

  if (loading) {
    return <LoadingState message="Loading factories..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={refresh} />;
  }

  return (
    <div className="content-page">
      <PageHeader
        eyebrow="INFRASTRUCTURE"
        title="Factories"
        description="Browse facilities connected to the MotorGuard platform."
      />

      {factories.length === 0 ? (
        <EmptyState
          title="No factories found"
          description="The backend currently has no registered factories."
        />
      ) : (
        <>
          <div className="list-summary">
            <span>{factories.length} registered facilities</span>
          </div>

          <div className="factory-grid">
            {factories.map((factory) => (
              <FactoryCard
                key={factory.id}
                factory={factory}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}