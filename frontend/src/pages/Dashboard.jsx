import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

import { getVolumes, getQualityStats } from "../api/client.js";
import { StatCard, Message } from "../components/common.jsx";

// Couleurs cohérentes avec la charte (jour / nuit).
const TYPE_COLORS = {
  day: "#c2701c",
  night: "#3b3486",
};

export default function Dashboard() {
  const [volumes, setVolumes] = useState(null);
  const [quality, setQuality] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // On charge en parallèle les volumes et les indicateurs qualité.
    Promise.all([getVolumes(), getQualityStats()])
      .then(([volumesData, qualityData]) => {
        setVolumes(volumesData);
        setQuality(qualityData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Message type="loading">Chargement des indicateurs…</Message>;
  }

  if (error) {
    return <Message type="error">{error}</Message>;
  }

  // Préparation des données pour les graphiques.
  const typeData = (volumes.by_train_type || []).map((row) => ({
    name: row.type_name === "night" ? "Nuit" : row.type_name === "day" ? "Jour" : row.type_name,
    rawType: row.type_name,
    value: Number(row.total_trips),
  }));

  const operatorData = (volumes.by_operator || [])
    .slice(0, 8)
    .map((row) => ({
      name: row.operator_name,
      trajets: Number(row.total_trips),
    }));

  const nightCount =
    typeData.find((d) => d.rawType === "night")?.value ?? 0;
  const dayCount = typeData.find((d) => d.rawType === "day")?.value ?? 0;

  return (
    <>
      <div className="page-head">
        <h1>Tableau de bord</h1>
        <p>
          Vue d'ensemble des dessertes ferroviaires européennes harmonisées :
          volumes, répartition entre trains de jour et de nuit, et contribution
          des opérateurs.
        </p>
      </div>

      {/* Indicateurs clés */}
      <section aria-label="Indicateurs clés" className="stat-grid">
        <StatCard label="Trajets recensés" value={volumes.total_trips} variant="accent" />
        <StatCard label="Trains de jour" value={dayCount} variant="day" />
        <StatCard label="Trains de nuit" value={nightCount} variant="night" />
        <StatCard
          label="Score qualité moyen"
          value={quality?.avg_quality_score ?? "—"}
          variant="accent"
        />
      </section>

      {/* Répartition jour / nuit */}
      <section className="panel" aria-label="Répartition jour / nuit">
        <h2>Répartition jour / nuit</h2>
        <div style={{ width: "100%", height: 280 }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={typeData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={95}
                label
              >
                {typeData.map((entry) => (
                  <Cell
                    key={entry.rawType}
                    fill={TYPE_COLORS[entry.rawType] || "#1d4e89"}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Volumes par opérateur */}
      <section className="panel" aria-label="Volumes de trajets par opérateur">
        <h2>Trajets par opérateur</h2>
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <BarChart data={operatorData} layout="vertical" margin={{ left: 30 }}>
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={140} />
              <Tooltip />
              <Bar dataKey="trajets" fill="#1d4e89" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </>
  );
}
