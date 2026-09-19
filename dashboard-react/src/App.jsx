import { useState, useEffect, useMemo } from "react";
import { getTickers, getProcessed, getPredictions, getAlerts, getLatestPredictions } from "./api";
import TickerSelector from "./components/TickerSelector";
import PriceChart from "./components/PriceChart";
import VolatilityChart from "./components/VolatilityChart";
import AlertsTable from "./components/AlertsTable";
import AlertSimulation from "./components/AlertSimulation";

const PAGE_ITEMS = [
  { id: "overview", label: "Overview" },
  { id: "market", label: "Market pulse" },
  { id: "alerts", label: "Alerts" },
  { id: "simulation", label: "Simulation" },
];

const formatPercent = (value, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/A";
  return `${(Number(value) * 100).toFixed(digits)}%`;
};

const formatCurrency = (value, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/A";
  return `$${Number(value).toFixed(digits)}`;
};

const SIMULATED_ALERTS_STORAGE_KEY = "insightlab-simulated-alerts";

function App() {
  const [tickers, setTickers] = useState([]);
  const [selected, setSelected] = useState("");
  const [page, setPage] = useState("overview");
  const [processed, setProcessed] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [simulatedAlerts, setSimulatedAlerts] = useState(() => {
    try {
      const stored = window.localStorage.getItem(SIMULATED_ALERTS_STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });
  const [marketSummary, setMarketSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    window.localStorage.setItem(
      SIMULATED_ALERTS_STORAGE_KEY,
      JSON.stringify(simulatedAlerts)
    );
  }, [simulatedAlerts]);

  useEffect(() => {
    let isMounted = true;

    const loadTickers = async () => {
      try {
        const list = await getTickers();
        if (!isMounted) return;

        setTickers(list);
        if (list.length > 0) {
          setSelected(list[0]);
        }
      } catch {
        if (!isMounted) return;
        setError("Impossible de charger la liste des actifs.");
      }
    };

    const loadMarketSummary = async () => {
      try {
        const data = await getLatestPredictions();
        if (isMounted) {
          setMarketSummary(data);
        }
      } catch {
        if (isMounted) console.error("Market summary could not be loaded");
      }
    };

    loadTickers();
    loadMarketSummary();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selected) return;

    let isMounted = true;

    const loadTickerData = async () => {
      try {
        setLoading(true);
        setError("");

        const [processedData, predictionData, alertData] = await Promise.all([
          getProcessed(selected),
          getPredictions(selected),
          getAlerts(selected),
        ]);

        if (!isMounted) return;

        setProcessed(processedData || []);
        setPredictions(predictionData || []);
        setAlerts(alertData || []);
        setLastUpdated(new Date());
      } catch {
        if (!isMounted) return;
        setError(`Impossible de charger les données du ticker ${selected}.`);
        setProcessed([]);
        setPredictions([]);
        setAlerts([]);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadTickerData();

    return () => {
      isMounted = false;
    };
  }, [selected, refreshKey]);

  useEffect(() => {
    if (!selected) return undefined;
    const refresh = window.setInterval(() => {
      setRefreshKey((current) => current + 1);
    }, 60000);
    return () => window.clearInterval(refresh);
  }, [selected]);

  const volatilityData = useMemo(() => {
    const predictionByDate = predictions.reduce((byDate, prediction) => {
      const date = prediction.prediction_ts?.slice(0, 10);
      if (date) byDate[date] = prediction.predicted_volatility;
      return byDate;
    }, {});

    return processed.map((item) => ({
      date: item.date,
      volatility_20d: item.volatility_20d,
      predicted_volatility: predictionByDate[item.date],
    }));
  }, [processed, predictions]);

  const lastClose = processed[processed.length - 1]?.close;
  const lastVol = processed[processed.length - 1]?.volatility_20d;
  const lastPred = predictions[predictions.length - 1]?.predicted_volatility;

  const overviewMetrics = [
    { label: "Prix de clôture", value: formatCurrency(lastClose) },
    { label: "Volatilité 20j", value: formatPercent(lastVol, 4) },
    { label: "Prédiction", value: formatPercent(lastPred, 4) },
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        {overviewMetrics.map((metric) => (
          <div key={metric.label} className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-slate-950/20 backdrop-blur-sm">
            <p className="text-xs font-medium uppercase tracking-[0.14em] text-slate-400">{metric.label}</p>
            <p className="mt-3 text-3xl font-semibold text-white">{metric.value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <PriceChart data={processed} ticker={selected} />
        <VolatilityChart data={volatilityData} ticker={selected} />
      </div>

      <AlertsTable alerts={alerts} />
    </div>
  );

  const renderMarket = () => (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {tickers.length === 0 ? (
          <div className="col-span-full rounded-2xl border border-dashed border-slate-700 bg-slate-900/60 p-8 text-center text-slate-300">
            Aucun actif disponible pour le moment.
          </div>
        ) : (
          tickers.map((ticker) => {
            const latest = marketSummary.find((item) => item.ticker === ticker);

            return (
              <button
                key={ticker}
                type="button"
                onClick={() => {
                  setSelected(ticker);
                  setPage("overview");
                }}
                className={`rounded-2xl border p-5 text-left shadow-xl transition ${
                  selected === ticker
                    ? "border-sky-500 bg-sky-500/10 shadow-sky-500/10"
                    : "border-slate-800 bg-slate-900/80 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <p className="text-lg font-semibold text-white">{ticker}</p>
                  <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 text-[10px] uppercase tracking-[0.14em] text-emerald-300">
                    Live
                  </span>
                </div>
                <p className="mt-4 text-sm text-slate-400">Latest prediction</p>
                <p className="mt-2 text-2xl font-semibold text-slate-100">{latest ? formatPercent(latest.predicted_volatility, 4) : "N/A"}</p>
              </button>
            );
          })
        )}
      </div>
    </div>
  );

  const renderAlerts = () => (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-slate-950/20">
        <p className="text-sm uppercase tracking-[0.14em] text-slate-400">Actif sélectionné</p>
        <div className="mt-3 flex items-center justify-between gap-4">
          <h2 className="text-2xl font-semibold text-white">{selected || "Aucun actif"}</h2>
          <TickerSelector tickers={tickers} selected={selected} onChange={setSelected} />
        </div>
      </div>
      <AlertsTable alerts={alerts} />
    </div>
  );

  const renderSimulation = () => (
    <div className="space-y-6">
      <AlertSimulation
        tickers={tickers}
        selected={selected}
        onCreate={(alert) => setSimulatedAlerts((current) => [alert, ...current])}
      />
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-slate-400">Historique local : {simulatedAlerts.length} alerte{simulatedAlerts.length !== 1 ? "s" : ""}</p>
        {simulatedAlerts.length > 0 && (
          <button
            type="button"
            onClick={() => setSimulatedAlerts([])}
            className="rounded-xl border border-red-500/30 px-3 py-2 text-sm font-medium text-red-300 transition hover:bg-red-500/10"
          >
            Effacer l’historique
          </button>
        )}
      </div>
      <AlertsTable alerts={simulatedAlerts} />
    </div>
  );

  return (
    <div className="min-h-screen px-4 py-8 text-slate-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-slate-950/30 backdrop-blur-sm">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.22em] text-sky-300">InsightLab</p>
              <h1 className="mt-2 text-3xl font-semibold text-white md:text-4xl">
                Volatility Intelligence Platform
              </h1>
            </div>

            <div className="flex w-full flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
              <div className="flex rounded-2xl border border-slate-800 bg-slate-950/70 p-1">
                {PAGE_ITEMS.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setPage(item.id)}
                    className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
                      page === item.id
                        ? "bg-sky-500 text-white shadow-lg shadow-sky-500/20"
                        : "text-slate-300 hover:bg-slate-800 hover:text-white"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>

              <TickerSelector tickers={tickers} selected={selected} onChange={setSelected} />
            </div>
          </div>
        </header>

        {error && (
          <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
            {error}
          </div>
        )}

        {loading && tickers.length > 0 && !error ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-10 text-center text-slate-300">
            Chargement des données du marché…
          </div>
        ) : null}

        {!selected && tickers.length === 0 && !loading && !error ? (
          <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/60 p-10 text-center text-slate-300">
            Aucune donnée disponible. Vérifiez le service API et les jobs d’ingestion.
          </div>
        ) : null}

        {selected && page === "overview" && (
          <>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/75 p-5 shadow-2xl shadow-slate-950/20">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.14em] text-slate-400">Focus</p>
                  <h2 className="mt-1 text-2xl font-semibold text-white">{selected}</h2>
                </div>
                <div className="text-right">
                  <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">
                    Market online
                  </span>
                  <p className="mt-2 text-xs text-slate-500">
                    {lastUpdated ? `Actualisé à ${lastUpdated.toLocaleTimeString()}` : "Synchronisation…"}
                  </p>
                </div>
              </div>
            </div>

            {renderOverview()}
          </>
        )}

        {selected && page === "market" && renderMarket()}
        {selected && page === "alerts" && renderAlerts()}
        {page === "simulation" && renderSimulation()}
      </div>
    </div>
  );
}

export default App;