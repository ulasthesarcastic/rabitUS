import { useEffect, useState } from "react";
import { connectionApi } from "../services/api";

const EMPTY_FORM = {
  name: "", type: "api",
  base_url: "", auth_type: "none", auth_config: {}, headers: {},
  db_type: "postgresql", db_host: "", db_port: 5432, db_name: "", db_user: "", db_password: "",
};

export default function ConnectionsPage() {
  const [connections, setConnections] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editing, setEditing] = useState(null);

  const load = () => connectionApi.list().then((r) => setConnections(r.data));

  useEffect(() => { load(); }, []);

  const openNew = () => { setForm(EMPTY_FORM); setEditing(null); setShowModal(true); };
  const openEdit = (c) => { setForm(c); setEditing(c.id); setShowModal(true); };

  const handleSave = async (e) => {
    e.preventDefault();
    if (editing) {
      await connectionApi.update(editing, form);
    } else {
      await connectionApi.create(form);
    }
    setShowModal(false);
    load();
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Bu bağlantıyı silmek istediğinize emin misiniz?")) return;
    await connectionApi.delete(id);
    load();
  };

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  return (
    <div>
      <div className="page-header">
        <h1>Bağlantılar</h1>
        <button className="btn btn-primary" onClick={openNew}>+ Yeni Bağlantı</button>
      </div>

      {connections.length === 0 ? (
        <div className="empty-state card">
          <p>Henüz bağlantı yok.</p>
          <p>İlk bağlantınızı ekleyerek başlayın.</p>
        </div>
      ) : (
        <div className="table-container card">
          <table>
            <thead>
              <tr>
                <th>Ad</th>
                <th>Tür</th>
                <th>Detay</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {connections.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td><span className="badge" style={{ background: c.type === "api" ? "#172554" : "#14532d", color: c.type === "api" ? "#60a5fa" : "#4ade80" }}>{c.type.toUpperCase()}</span></td>
                  <td style={{ color: "#64748b" }}>{c.type === "api" ? c.base_url : `${c.db_host}:${c.db_port}/${c.db_name}`}</td>
                  <td>
                    <button className="btn btn-secondary btn-sm" onClick={() => openEdit(c)}>Düzenle</button>{" "}
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(c.id)}>Sil</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editing ? "Bağlantı Düzenle" : "Yeni Bağlantı"}</h2>
              <button className="btn btn-secondary btn-sm" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <form onSubmit={handleSave}>
              <div className="form-row">
                <div className="form-group">
                  <label>Ad</label>
                  <input value={form.name} onChange={(e) => set("name", e.target.value)} required />
                </div>
                <div className="form-group">
                  <label>Tür</label>
                  <select value={form.type} onChange={(e) => set("type", e.target.value)}>
                    <option value="api">REST API</option>
                    <option value="db">Veritabanı</option>
                  </select>
                </div>
              </div>

              {form.type === "api" ? (
                <>
                  <div className="form-group">
                    <label>Base URL</label>
                    <input value={form.base_url || ""} onChange={(e) => set("base_url", e.target.value)} placeholder="https://api.example.com" />
                  </div>
                  <div className="form-group">
                    <label>Auth Type</label>
                    <select value={form.auth_type || "none"} onChange={(e) => set("auth_type", e.target.value)}>
                      <option value="none">Yok</option>
                      <option value="bearer">Bearer Token</option>
                      <option value="basic">Basic Auth</option>
                      <option value="api_key">API Key</option>
                    </select>
                  </div>
                  {form.auth_type === "bearer" && (
                    <div className="form-group">
                      <label>Token</label>
                      <input type="password" value={form.auth_config?.token || ""} onChange={(e) => set("auth_config", { token: e.target.value })} />
                    </div>
                  )}
                  {form.auth_type === "basic" && (
                    <div className="form-row">
                      <div className="form-group">
                        <label>Username</label>
                        <input value={form.auth_config?.username || ""} onChange={(e) => set("auth_config", { ...form.auth_config, username: e.target.value })} />
                      </div>
                      <div className="form-group">
                        <label>Password</label>
                        <input type="password" value={form.auth_config?.password || ""} onChange={(e) => set("auth_config", { ...form.auth_config, password: e.target.value })} />
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="form-row">
                    <div className="form-group">
                      <label>DB Tipi</label>
                      <select value={form.db_type || "postgresql"} onChange={(e) => set("db_type", e.target.value)}>
                        <option value="postgresql">PostgreSQL</option>
                        <option value="mysql">MySQL</option>
                        <option value="mssql">MS SQL Server</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Port</label>
                      <input type="number" value={form.db_port || ""} onChange={(e) => set("db_port", parseInt(e.target.value))} />
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Host</label>
                    <input value={form.db_host || ""} onChange={(e) => set("db_host", e.target.value)} placeholder="localhost" />
                  </div>
                  <div className="form-group">
                    <label>Veritabanı Adı</label>
                    <input value={form.db_name || ""} onChange={(e) => set("db_name", e.target.value)} />
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Kullanıcı</label>
                      <input value={form.db_user || ""} onChange={(e) => set("db_user", e.target.value)} />
                    </div>
                    <div className="form-group">
                      <label>Şifre</label>
                      <input type="password" value={form.db_password || ""} onChange={(e) => set("db_password", e.target.value)} />
                    </div>
                  </div>
                </>
              )}

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>İptal</button>
                <button type="submit" className="btn btn-primary">Kaydet</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
