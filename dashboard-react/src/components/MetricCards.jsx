const formatValue = (value, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "N/A";
  }
  return Number(value).toFixed(digits);
};

function Card({ label, value, suffix = "" }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-slate-950/20 backdrop-blur-sm">
      <p className="text-xs font-medium uppercase tracking-[0.14em] text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-white">
        {value ?? "N/A"}
        {suffix}
      </p>
    </div>
  );
}

export default function MetricCards({ lastClose, lastVol, lastPred }) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Card label="Dernier cours" value={lastClose != null ? `$${formatValue(lastClose, 2)}` : "N/A"} />
      <Card label="Volatilité 20j" value={lastVol != null ? formatValue(lastVol, 4) : "N/A"} suffix="%" />
      <Card label="Dernière prédiction" value={lastPred != null ? formatValue(lastPred, 4) : "N/A"} suffix="%" />
    </div>
  );
}