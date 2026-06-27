// Reference kit (styleguide): accessibility icons + UI states. Not part of the
// main flows — useful for designers/devs verifying components.
import { AudioIcon, CheckIcon, InfoIcon, LibrasIcon, WheelchairIcon } from "../lib/icons";
import { EmptyState, ErrorState, SkeletonGrid } from "../components/states";
import { NotFound } from "./Detail";

function FeatureChip({
  icon,
  label,
  available,
}: {
  icon: React.ReactNode;
  label: string;
  available: boolean;
}) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        fontSize: 13,
        fontWeight: 600,
        padding: "6px 11px",
        borderRadius: 999,
        color: available ? "var(--teal-tx)" : "#8A8275",
        background: available ? "var(--teal-bg)" : "#F4F1EA",
        border: `1px solid ${available ? "var(--teal-bd)" : "#E6DFCF"}`,
      }}
    >
      {icon}
      {label}
      <span style={{ marginLeft: 2, opacity: 0.85 }}>
        {available ? <CheckIcon size={12} /> : "·"}
      </span>
      <span className="sr-only">{available ? "Disponível" : "Não informado"}</span>
    </span>
  );
}

const FEATURES = [
  { label: "Libras", icon: <LibrasIcon size={15} /> },
  { label: "Audiodescrição", icon: <AudioIcon size={15} /> },
  { label: "Cadeirante", icon: <WheelchairIcon size={15} /> },
  { label: "Assento amplo", icon: <InfoIcon size={15} /> },
];

const section = { marginBottom: 40 } as const;
const h2 = { fontSize: 24, margin: "0 0 14px" } as const;

export function Kit() {
  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 8 }}>
      <h1 style={{ fontSize: 40, letterSpacing: "-.015em", margin: "0 0 8px" }}>Kit de componentes</h1>
      <p style={{ fontSize: 17, color: "var(--cm)", margin: "0 0 32px", maxWidth: 620 }}>
        Referência visual dos ícones de acessibilidade e dos estados da interface.
      </p>

      <section style={section}>
        <h2 style={h2}>Ícones de acessibilidade</h2>
        <p style={{ fontSize: 14, color: "var(--cm2)", margin: "0 0 14px" }}>
          Cada selo combina ícone + rótulo textual + estado, nunca dependendo só de cor.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 12 }}>
          {FEATURES.map((f) => (
            <FeatureChip key={f.label} icon={f.icon} label={f.label} available />
          ))}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
          {FEATURES.map((f) => (
            <FeatureChip key={f.label} icon={f.icon} label={f.label} available={false} />
          ))}
        </div>
      </section>

      <section style={section}>
        <h2 style={h2}>Carregando (skeleton)</h2>
        <SkeletonGrid count={3} />
      </section>

      <section style={section}>
        <h2 style={h2}>Vazio</h2>
        <div style={{ display: "grid" }}>
          <EmptyState />
        </div>
      </section>

      <section style={section}>
        <h2 style={h2}>Erro / offline</h2>
        <div style={{ display: "grid" }}>
          <ErrorState />
        </div>
      </section>

      <section style={section}>
        <h2 style={h2}>404</h2>
        <div style={{ border: "1px dashed var(--cl2)", borderRadius: 14 }}>
          <NotFound />
        </div>
      </section>
    </div>
  );
}
