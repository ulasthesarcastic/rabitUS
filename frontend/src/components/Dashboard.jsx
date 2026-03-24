import { useEffect, useState } from "react";
import { connectionApi, flowApi } from "../services/api";

export default function Dashboard() {
  const [stats, setStats] = useState({ connections: 0, flows: 0, activeFlows: 0 });

  useEffect(() => {
    Promise.all([connectionApi.list(), flowApi.list()]).then(([connRes, flowRes]) => {
      const flows = flowRes.data;
      setStats({
        connections: connRes.data.length,
        flows: flows.length,
        activeFlows: flows.filter((f) => f.active).length,
      });
    });
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
        <div className="card">
          <div style={{ color: "#64748b", fontSize: "0.85rem" }}>Bağlantılar</div>
          <div style={{ fontSize: "2rem", fontWeight: 700, marginTop: "0.5rem" }}>{stats.connections}</div>
        </div>
        <div className="card">
          <div style={{ color: "#64748b", fontSize: "0.85rem" }}>Toplam Flow</div>
          <div style={{ fontSize: "2rem", fontWeight: 700, marginTop: "0.5rem" }}>{stats.flows}</div>
        </div>
        <div className="card">
          <div style={{ color: "#64748b", fontSize: "0.85rem" }}>Aktif Flow</div>
          <div style={{ fontSize: "2rem", fontWeight: 700, marginTop: "0.5rem", color: "#4ade80" }}>
            {stats.activeFlows}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h3 style={{ marginBottom: "1rem" }}>Hızlı Başlangıç</h3>
        <ol style={{ paddingLeft: "1.25rem", lineHeight: 2, color: "#94a3b8" }}>
          <li><strong>Bağlantı tanımla</strong> — API endpoint veya DB credentials gir</li>
          <li><strong>RQL yaz</strong> — mapping, logic, tetikleyici tanımla</li>
          <li><strong>Test et</strong> — gerçek veriyle dene, hataları gör</li>
          <li><strong>Canlıya al</strong> — tetikleyici devreye girer</li>
          <li><strong>İzle</strong> — log, hata takibi, kaç kayıt geçti</li>
        </ol>
      </div>
    </div>
  );
}
