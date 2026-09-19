import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function VolatilityChart({ data, ticker }) {
  const formatPercent = (value) => `${(Number(value) * 100).toFixed(2)}%`;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-slate-950/20">
      <h2 className="mb-3 text-lg font-semibold text-white">{ticker} — Volatilité réalisée vs prédite</h2>
      {data.length === 0 ? (
        <div className="flex h-[280px] items-center justify-center rounded-xl border border-dashed border-slate-700 text-sm text-slate-400">
          Aucune donnée de volatilité disponible.
        </div>
      ) : (
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94a3b8" }} minTickGap={30} axisLine={{ stroke: "#334155" }} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} tickFormatter={formatPercent} axisLine={{ stroke: "#334155" }} tickLine={false} />
          <Tooltip formatter={(value) => formatPercent(value)} contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 12, color: "#e2e8f0" }} />
          <Legend wrapperStyle={{ color: "#cbd5e1", paddingTop: 12 }} />
          <Line type="monotone" dataKey="volatility_20d" stroke="#38bdf8" dot={false} name="Volatilité réalisée (20j)" strokeWidth={2} connectNulls />
          <Line type="monotone" dataKey="predicted_volatility" stroke="#fb7185" dot={{ r: 3 }} name="Volatilité prédite" strokeWidth={2} connectNulls />
        </LineChart>
      </ResponsiveContainer>
      )}
    </div>
  );
}