import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import { useApiHealth } from "../../hooks/useApiHealth";

export default function AppLayout() {
  const { status } = useApiHealth();

  return (
    <div className="app-shell">
      <Navbar apiStatus={status} />

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="app-footer">
        <span>MotorGuard</span>
        <span>Industrial Monitoring & Predictive Maintenance</span>
      </footer>
    </div>
  );
}