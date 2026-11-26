import { NavLink } from "react-router-dom";
import {
  Activity,
  Factory,
  LayoutDashboard,
  Boxes,
} from "lucide-react";
import StatusBadge from "../common/StatusBadge";
import type { ApiStatus } from "../../hooks/useApiHealth";

interface NavbarProps {
  apiStatus: ApiStatus;
}

export default function Navbar({ apiStatus }: NavbarProps) {
  return (
    <header className="navbar">
      <NavLink to="/" className="brand">
        <div className="brand-icon">
          <Activity size={20} />
        </div>

        <div className="brand-text">
          <span className="brand-name">MotorGuard</span>
          <span className="brand-subtitle">Industrial Intelligence</span>
        </div>
      </NavLink>

      <nav className="nav-links">
        <NavLink to="/" end className="nav-link">
          <LayoutDashboard size={17} />
          Overview
        </NavLink>

        <NavLink to="/factories" className="nav-link">
          <Factory size={17} />
          Factories
        </NavLink>

        <NavLink to="/motors" className="nav-link">
          <Boxes size={17} />
          Motors
        </NavLink>
      </nav>

      <div className="nav-status">
        <StatusBadge
          label={
            apiStatus === "online"
              ? "API Connected"
              : apiStatus === "checking"
                ? "Connecting"
                : "API Offline"
          }
          variant={
            apiStatus === "online"
              ? "success"
              : apiStatus === "checking"
                ? "neutral"
                : "danger"
          }
        />
      </div>
    </header>
  );
}