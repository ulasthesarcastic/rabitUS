import { NavLink } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>rabit<span>US</span></h2>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/connections">Bağlantılar</NavLink>
        <NavLink to="/flows">Flow'lar</NavLink>
      </nav>

      <div className="sidebar-footer">
        <small style={{ color: "#64748b", display: "block", marginBottom: "0.5rem" }}>
          {user?.full_name}
        </small>
        <button onClick={logout}>Çıkış Yap</button>
      </div>
    </aside>
  );
}
