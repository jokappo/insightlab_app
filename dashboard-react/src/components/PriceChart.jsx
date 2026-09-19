import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function PriceChart({ data, ticker }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-slate-950/20">
      <h2 className="mb-3 text-lg font-semibold text-white">{ticker} — Prix & moyennes mobiles</h2>
      {data.length === 0 ? (
        <div className="flex h-[320px] items-center justify-center rounded-xl border border-dashed border-slate-700 text-sm text-slate-400">
          Aucun historique disponible pour cet actif.
        </div>
      ) : (
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94a3b8" }} minTickGap={30} axisLine={{ stroke: "#334155" }} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} domain={["auto", "auto"]} axisLine={{ stroke: "#334155" }} tickLine={false} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 12, color: "#e2e8f0" }} />
          <Legend wrapperStyle={{ color: "#cbd5e1", paddingTop: 12 }} />
          <Line type="monotone" dataKey="close" stroke="#38bdf8" dot={false} name="Clôture" strokeWidth={2} connectNulls />
          <Line type="monotone" dataKey="ma_5d" stroke="#fbbf24" dot={false} name="MM 5j" connectNulls />
          <Line type="monotone" dataKey="ma_10d" stroke="#34d399" dot={false} name="MM 10j" connectNulls />
          <Line type="monotone" dataKey="ma_20d" stroke="#fb7185" dot={false} name="MM 20j" connectNulls />
        </LineChart>
      </ResponsiveContainer>
      )}
    </div>
  );
}