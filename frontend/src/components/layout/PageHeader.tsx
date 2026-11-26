import type { ReactNode } from "react";

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}

export default function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: PageHeaderProps) {
  return (
    <div className="page-header">
      <div>
        {eyebrow && <div className="page-eyebrow">{eyebrow}</div>}

        <h1>{title}</h1>

        {description && (
          <p className="page-description">{description}</p>
        )}
      </div>

      {action && <div className="page-header-action">{action}</div>}
    </div>
  );
}