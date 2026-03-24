import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import "../styles/Login.css";

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  if (user) return <Navigate to="/" />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError("Geçersiz kullanıcı adı veya şifre");
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="login-logo">
          <h1>rabit<span>US</span></h1>
          <p>Integration Platform</p>
        </div>
        {error && <div className="login-error">{error}</div>}
        <input
          type="text"
          placeholder="Kullanıcı adı"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
        />
        <input
          type="password"
          placeholder="Şifre"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Giriş Yap</button>
      </form>
    </div>
  );
}
