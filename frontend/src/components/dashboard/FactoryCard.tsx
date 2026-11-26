import { ArrowUpRight, Factory } from "lucide-react";
import { Link } from "react-router-dom";
import type { Factory as FactoryType } from "../../types/factory";

interface FactoryCardProps {
  factory: FactoryType;
}

export default function FactoryCard({ factory }: FactoryCardProps) {
  return (
    <Link
      to={`/factories/${encodeURIComponent(factory.id)}`}
      className="factory-card"
    >
      <div className="factory-card-icon">
        <Factory size={21} />
      </div>

      <div className="factory-card-content">
        <div className="factory-card-title-row">
          <h3>{factory.name}</h3>
          <ArrowUpRight size={18} className="factory-arrow" />
        </div>

        <p className="factory-id">ID · {factory.id}</p>

        <div className="factory-card-footer">
          <span>View facility</span>
          <span className="factory-card-link">Explore →</span>
        </div>
      </div>
    </Link>
  );
}