import { useEffect, useState } from "react";
import { connectionApi, flowApi } from "../services/api";

export default function FlowsPage() {
  const [flows, setFlows] = useState([]);
  const [connections, setConnections] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showRuns, setShowRuns] = useState(null);
  const [runs, setRuns] = useState([]);
  const [editing, setEditing] = useState(null);
  const [validation, setValidation] = useState(null);
  const [form, setForm] = useState({
    name: "", rql: "", source_connection_id: "", target_connection_id: "",
    source_path: "", target_path: "",
  });

  const load = () => flowApi.list().then((r) => setFlows(r.data));

  useEffect(() => {
    load();
    connectionApi.list().then((r) => setConnections(r.data));
  }, []);

  const openNew = () => {
    setForm({ name: "", rql: "", source_connection_id: "", target_connection_id: "", source_path: "", target_path: "" });
    setEditing(null);
    setValidation(null);
    setShowModal(true);
  };

  const openEdit = (f) => {
    setForm(f);
    setEditing(f.id);
    setValidation(null);
    setShowModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (editing) {
      await flowApi.update(editing, form);
    } else {
      await flowApi.create(form);
    }
    setShowModal(false);
    load();
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Bu flow'u silmek istediğinize emin misiniz?")) return;
    await flowApi.delete(id);
    load();
  };

  const handleRun = async (id) => {
    await flowApi.run(id);
    load();
  };

  const handleValidate = async () => {
    const res = await flowApi.validate(form.rql);
    setValidation(res.data);
  };

  const viewRuns = async (flow) => {
    const res = await flowApi.runs(flow.id);
    setRuns(res.data);
    setShowRuns(flow);
  };

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  const RQL_PLACEHOLDER = `# Bağlantı tanımı
SOURCE api:trendyol/orders
TARGET db:logo/tbl_fatura

# Alan mapping
source.siparis_no → target.fatura_no
source.musteri_adi → target.cari_unvan
source.tutar → target.toplam_tutar

# Logic
IF source.tutar > 1000 THEN target.kategori = "premium"
IF source.musteri_id IS EMPTY THEN SKIP

# Tetikleyici
TRIGGER every 15min`;

  return (
    <div>
      <div className="page-header">
        <h1>Flow'lar</h1>
        <button className="btn btn-primary" onClick={openNew}>+ Yeni Flow</button>
      </div>

      {flows.length === 0 ? (
        <div className="empty-state card">
          <p>Henüz flow yok.</p>
          <p>İlk flow'unuzu oluşturarak iki sistemi entegre edin.</p>
        </div>
      ) : (
        <div className="table-container card">
          <table>
            <thead>
              <tr>
                <th>Ad</th>
                <th>Kaynak</th>
                <th>Hedef</th>
                <th>Tetikleyici</th>
                <th>Durum</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {flows.map((f) => (
                <tr key={f.id}>
                  <td>{f.name}</td>
                  <td style={{ color: "#64748b" }}>{f.source_path}</td>
                  <td style={{ color: "#64748b" }}>{f.target_path}</td>
                  <td>
                    {f.trigger_type === "interval"
                      ? `Her ${f.trigger_interval_minutes} dk`
                      : "Manuel"}
                  </td>
                  <td>
                    <span className={`badge ${f.active ? "badge-success" : "badge-inactive"}`}>
                      {f.active ? "Aktif" : "Pasif"}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-success btn-sm" onClick={() => handleRun(f.id)} title="Çalıştır">▶</button>{" "}
                    <button className="btn btn-secondary btn-sm" onClick={() => viewRuns(f)}>Loglar</button>{" "}
                    <button className="btn btn-secondary btn-sm" onClick={() => openEdit(f)}>Düzenle</button>{" "}
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(f.id)}>Sil</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* New/Edit Flow Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ width: 700 }}>
            <div className="modal-header">
              <h2>{editing ? "Flow Düzenle" : "Yeni Flow"}</h2>
              <button className="btn btn-secondary btn-sm" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <form onSubmit={handleSave}>
              <div className="form-group">
                <label>Flow Adı</label>
                <input value={form.name} onChange={(e) => set("name", e.target.value)} required />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Kaynak Bağlantı</label>
                  <select value={form.source_connection_id} onChange={(e) => set("source_connection_id", e.target.value)} required>
                    <option value="">Seçin...</option>
                    {connections.map((c) => <option key={c.id} value={c.id}>{c.name} ({c.type})</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Kaynak Path</label>
                  <input value={form.source_path} onChange={(e) => set("source_path", e.target.value)} placeholder="orders veya tbl_siparis" required />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Hedef Bağlantı</label>
                  <select value={form.target_connection_id} onChange={(e) => set("target_connection_id", e.target.value)} required>
                    <option value="">Seçin...</option>
                    {connections.map((c) => <option key={c.id} value={c.id}>{c.name} ({c.type})</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Hedef Path</label>
                  <input value={form.target_path} onChange={(e) => set("target_path", e.target.value)} placeholder="invoices veya tbl_fatura" required />
                </div>
              </div>

              <div className="form-group">
                <label>
                  RQL
                  <button type="button" className="btn btn-secondary btn-sm" style={{ marginLeft: "0.5rem" }} onClick={handleValidate}>
                    Doğrula
                  </button>
                </label>
                <textarea
                  value={form.rql}
                  onChange={(e) => { set("rql", e.target.value); setValidation(null); }}
                  rows={12}
                  placeholder={RQL_PLACEHOLDER}
                  style={{ fontFamily: "monospace", fontSize: "0.85rem" }}
                  required
                />
              </div>

              {validation && (
                <div className="card" style={{ background: validation.valid ? "#052e16" : "#450a0a", borderColor: validation.valid ? "#166534" : "#991b1b" }}>
                  {validation.valid ? (
                    <div style={{ color: "#4ade80", fontSize: "0.85rem" }}>
                      RQL geçerli — {validation.mapping_count} mapping, {validation.rule_count} kural, tetikleyici: {validation.trigger_type}
                    </div>
                  ) : (
                    <div style={{ color: "#f87171", fontSize: "0.85rem" }}>Hata: {validation.error}</div>
                  )}
                </div>
              )}

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>İptal</button>
                <button type="submit" className="btn btn-primary">Kaydet</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Run History Modal */}
      {showRuns && (
        <div className="modal-overlay" onClick={() => setShowRuns(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ width: 700 }}>
            <div className="modal-header">
              <h2>Çalışma Geçmişi — {showRuns.name}</h2>
              <button className="btn btn-secondary btn-sm" onClick={() => setShowRuns(null)}>✕</button>
            </div>

            {runs.length === 0 ? (
              <div className="empty-state"><p>Henüz çalışma kaydı yok.</p></div>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Tarih</th>
                      <th>Durum</th>
                      <th>İşlenen</th>
                      <th>Hata</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.map((r) => (
                      <tr key={r.id}>
                        <td>{new Date(r.started_at).toLocaleString("tr-TR")}</td>
                        <td>
                          <span className={`badge badge-${r.status === "success" ? "success" : r.status === "error" ? "error" : "running"}`}>
                            {r.status}
                          </span>
                        </td>
                        <td>{r.records_processed}</td>
                        <td style={{ color: "#f87171", fontSize: "0.8rem" }}>{r.error_message || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
