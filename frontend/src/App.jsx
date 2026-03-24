import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import LoginPage from "./auth/LoginPage";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import ConnectionsPage from "./components/ConnectionsPage";
import FlowsPage from "./components/FlowsPage";
import "./styles/App.css";

function ProtectedLayout() {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (!user) return <Navigate to="/login" />;

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/connections" element={<ConnectionsPage />} />
          <Route path="/flows" element={<FlowsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={<ProtectedLayout />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
