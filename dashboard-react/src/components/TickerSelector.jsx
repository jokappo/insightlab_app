export default function TickerSelector({ tickers, selected, onChange }) {
  const fallbackValue = selected || "";

  return (
    <select
      value={fallbackValue}
      onChange={(e) => onChange(e.target.value)}
      disabled={tickers.length === 0}
      className="w-full rounded-xl border border-slate-700 bg-slate-900/80 px-3 py-2.5 text-sm font-medium text-slate-100 shadow-lg shadow-slate-950/20 outline-none transition hover:border-sky-400 focus:border-sky-400 focus:ring-2 focus:ring-sky-500/50 disabled:cursor-not-allowed disabled:opacity-60 md:w-52"
    >
      {tickers.length === 0 && <option value="">Aucun actif</option>}
      {tickers.map((t) => (
        <option key={t} value={t}>{t}</option>
      ))}
    </select>
  );
}