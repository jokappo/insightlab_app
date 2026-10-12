import { useState } from "react";
import { simulateMarketShock } from "../api";

const DEFAULT_SHOCK = "-8";

export default function AlertSimulation({ tickers, selected, onCreate, onComplete }) {
  const [ticker, setTicker] = useState(selected || tickers[0] || "");
  const [shockPercent, setShockPercent] = useState(DEFAULT_SHOCK);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setRunning(true);
    setError("");
    setResult(null);

    try {
      const simulationResult = await simulateMarketShock({
        ticker,
        shock_percent: Number(shockPercent),
      });
      setResult(simulationResult);
      simulationResult.alerts.forEach((alert) => onCreate({ ...alert, isSimulation: true }));
      onComplete(simulationResult);
    } catch {
      setError("La simulation n’a pas pu exécuter le pipeline de prédiction.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
      <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl shadow-slate-950/20">
        <div className="mb-6">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-amber-300">Mode démonstration</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Simuler une alerte</h2>
          <p className="mt-2 text-sm leading-6 text-slate-400">
            Injecte une cotation synthétique dans le Data Lake, puis exécute le même pipeline que la production : features, prédiction et détection d’alerte.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-300">Actif</span>
            <select
              value={ticker}
              onChange={(event) => setTicker(event.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3 text-slate-100 outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/30"
              required
            >
              {tickers.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-300">Choc de prix simulé (%)</span>
            <input
              type="number"
              min="-50"
              max="50"
              step="0.1"
              value={shockPercent}
              onChange={(event) => setShockPercent(event.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3 text-slate-100 outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/30"
              required
            />
          </label>

          <button
            type="submit"
            disabled={running || !ticker}
            className="w-full rounded-xl bg-amber-400 px-4 py-3 font-semibold text-slate-950 transition hover:bg-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-300 focus:ring-offset-2 focus:ring-offset-slate-900"
          >
            {running ? "Exécution du pipeline…" : "Injecter et lancer la simulation"}
          </button>
        </form>

        {error && <p className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">{error}</p>}
        {result && (
          <div className="mt-4 space-y-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-100">
            <p className="font-semibold">Donnée injectée dans le Data Lake.</p>
            <p>Prix simulé : {(result.simulation.simulated_close ?? 0).toFixed(2)}</p>
            <p>Prédiction réelle : {(Number(result.prediction.predicted_volatility) * 100).toFixed(4)}%</p>
            <p>{result.alerts.length ? "Alerte déclenchée." : "Aucune alerte déclenchée pour ce scénario."}</p>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-6 shadow-2xl shadow-slate-950/20">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-amber-300">Scénario de présentation</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Détection de risque élevé</h2>
          </div>
          <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-200">Factice</span>
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Seuil d’alerte</p>
            <p className="mt-2 text-2xl font-semibold text-white">Z-score &gt; 2</p>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Valeur proposée</p>
            <p className="mt-2 text-2xl font-semibold text-amber-300">-8,00 %</p>
          </div>
        </div>
        <p className="mt-6 text-sm leading-6 text-slate-300">
          Cette action modifie volontairement `raw_streaming`, `predictions` et éventuellement `alerts`. Utilise-la uniquement sur un environnement de démonstration.
        </p>
      </section>
    </div>
  );
}
