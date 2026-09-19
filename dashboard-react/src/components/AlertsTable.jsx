export default function AlertsTable({ alerts }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-slate-950/20">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-white">🚨 Alertes récentes</h2>
        <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-300">
          {alerts.length} signal{alerts.length > 1 ? "s" : ""}
        </span>
      </div>
      {alerts.length === 0 ? (
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm text-emerald-200">
          Aucune alerte active pour cet actif. Le moteur de détection est stable.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-800">
          <table className="w-full text-sm text-left text-slate-200">
            <thead className="bg-slate-950/70 text-xs uppercase tracking-[0.12em] text-slate-400">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Volatilité prédite</th>
              <th className="px-4 py-3">Z-score</th>
              <th className="px-4 py-3">Message</th>
            </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr key={a.id ?? `${a.alert_ts}-${a.message}`} className="border-t border-slate-800 bg-slate-900/30">
                  <td className="px-4 py-3">{a.alert_ts ? new Date(a.alert_ts).toLocaleString() : "N/A"}</td>
                  <td className="px-4 py-3">{a.predicted_volatility != null ? `${(Number(a.predicted_volatility) * 100).toFixed(4)}%` : "N/A"}</td>
                  <td className="px-4 py-3">{a.zscore != null ? Number(a.zscore).toFixed(2) : "N/A"}</td>
                  <td className="px-4 py-3 text-red-300">
                    {a.isSimulation && <span className="mr-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-1 text-[10px] uppercase tracking-[0.12em] text-amber-300">Simulation</span>}
                    {a.message || "Alerte détectée"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
