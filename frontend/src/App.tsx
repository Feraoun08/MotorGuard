
import { Routes, Route } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";

import DashboardPage from "./pages/DashboardPage";
import FactoriesPage from "./pages/FactoriesPage";
import FactoryDetailsPage from "./pages/FactoryDetailsPage";
import ProductionLinePage from "./pages/ProductionLinePage";
import MotorsPage from "./pages/MotorsPage";
import NotFoundPage from "./pages/NotFoundPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/factories" element={<FactoriesPage />} />

        <Route
          path="/factories/:factoryId"
          element={<FactoryDetailsPage />}
        />

        <Route
          path="/factories/:factoryId/lines/:lineId"
          element={<ProductionLinePage />}
        />

        <Route path="/motors" element={<MotorsPage />} />

        <Route
          path="/factories/:factoryId/motors/:motorId"
          element={<NotFoundPage />}
        />

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
