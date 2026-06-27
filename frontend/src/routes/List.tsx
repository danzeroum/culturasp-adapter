import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { toEventVM, type EventVM } from "../lib/adapter";
import { AccessibilityIcon } from "../lib/icons";
import { useEvents } from "../lib/queries";
import { EventCard } from "../components/EventCard";
import { EmptyState, ErrorState, SkeletonGrid } from "../components/states";

function Switch({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={onChange}
      style={{
        all: "unset",
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        gap: 10,
        width: "100%",
        minHeight: 44,
      }}
    >
      <span
        style={{
          width: 38,
          height: 22,
          borderRadius: 999,
          background: checked ? "var(--teal)" : "#D8CFBC",
          position: "relative",
          flex: "none",
          transition: "background .15s",
        }}
      >
        <span
          style={{
            position: "absolute",
            top: 2,
            left: checked ? 18 : 2,
            width: 18,
            height: 18,
            borderRadius: "50%",
            background: "#FCFBF8",
            boxShadow: "0 1px 2px rgba(0,0,0,.3)",
            transition: "left .15s",
          }}
        />
      </span>
      <span style={{ fontSize: 13.5, fontWeight: 600, color: "var(--ct)" }}>{label}</span>
    </button>
  );
}

const divider = <div style={{ height: 1, background: "var(--cl)" }} />;

export function List() {
  const [params, setParams] = useSearchParams();
  const accessible = params.get("accessible") === "true";
  const weekend = params.get("weekend") === "true";
  const free = params.get("free") === "true";
  const tipo = params.getAll("tipo"); // 'Concerto' | 'Exposição'

  const setFlag = (key: string, on: boolean) => {
    const next = new URLSearchParams(params);
    if (on) next.set(key, "true");
    else next.delete(key);
    setParams(next, { replace: true });
  };
  const toggleTipo = (t: string) => {
    const next = new URLSearchParams(params);
    const current = next.getAll("tipo");
    next.delete("tipo");
    const updated = current.includes(t) ? current.filter((x) => x !== t) : [...current, t];
    updated.forEach((x) => next.append("tipo", x));
    setParams(next, { replace: true });
  };
  const clear = () => setParams(new URLSearchParams(), { replace: true });

  // Server supports `accessible`; weekend/free/tipo are applied client-side.
  const { data, isLoading, isError, refetch } = useEvents({ accessible: accessible || undefined, limit: 60 });

  const filtered: EventVM[] = useMemo(() => {
    let vms = (data ?? []).map(toEventVM);
    if (weekend) vms = vms.filter((v) => v.weekend);
    if (free) vms = vms.filter((v) => v.free);
    if (tipo.length) vms = vms.filter((v) => tipo.includes(v.typeLabel));
    vms.sort((a, b) => (a.isUndated ? 1 : 0) - (b.isUndated ? 1 : 0));
    return vms;
  }, [data, weekend, free, tipo]);

  const activeBits = [accessible && "acessível", weekend && "fim de semana", free && "gratuito", ...tipo.map((t) => t.toLowerCase())].filter(Boolean);
  const summary = activeBits.length ? ` · ${activeBits.join(", ")}` : "";

  return (
    <div className="container" style={{ paddingTop: 36, paddingBottom: 8, display: "grid", gridTemplateColumns: "268px 1fr", gap: 32, alignItems: "start" }}>
      {/* Filtros */}
      <aside
        aria-label="Filtros"
        style={{
          position: "sticky",
          top: 90,
          background: "var(--cs)",
          border: "1px solid var(--cl)",
          borderRadius: 12,
          padding: 22,
          display: "flex",
          flexDirection: "column",
          gap: 20,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: 13, fontWeight: 800, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--ct)" }}>
            Filtros
          </span>
          <button type="button" onClick={clear} style={{ all: "unset", cursor: "pointer", fontSize: 13, fontWeight: 600, color: "var(--brand)" }}>
            Limpar
          </button>
        </div>

        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color: "var(--cm)", marginBottom: 11 }}>Período</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
            <button
              type="button"
              aria-pressed={weekend}
              onClick={() => setFlag("weekend", !weekend)}
              style={{
                all: "unset",
                cursor: "pointer",
                fontSize: 13,
                fontWeight: 600,
                padding: "7px 12px",
                borderRadius: 8,
                border: `1px solid ${weekend ? "var(--weekend-bd)" : "var(--cl2)"}`,
                color: weekend ? "var(--weekend-tx)" : "var(--cm2)",
                background: weekend ? "var(--weekend-bg)" : "var(--cb)",
              }}
            >
              Fim de semana
            </button>
          </div>
        </div>

        {divider}

        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 13, fontWeight: 700, color: "var(--navacc)", marginBottom: 11 }}>
            <AccessibilityIcon size={15} />
            Acessibilidade
          </div>
          <Switch checked={accessible} onChange={() => setFlag("accessible", !accessible)} label="Com recursos de acessibilidade" />
          <p style={{ fontSize: 12, color: "var(--cf)", margin: "8px 2px 0", lineHeight: 1.4 }}>
            Libras, audiodescrição ou assentos para cadeirantes.
          </p>
        </div>

        {divider}

        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color: "var(--cm)", marginBottom: 11 }}>Tipo</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
            {["Concerto", "Exposição"].map((t) => (
              <label key={t} style={{ display: "flex", alignItems: "center", gap: 9, fontSize: 14, color: "var(--ct)", cursor: "pointer", minHeight: 28 }}>
                <input type="checkbox" checked={tipo.includes(t)} onChange={() => toggleTipo(t)} />
                {t}
              </label>
            ))}
          </div>
        </div>

        {divider}

        <Switch checked={free} onChange={() => setFlag("free", !free)} label="Somente gratuitos" />
      </aside>

      {/* Resultados */}
      <div>
        <h1 style={{ fontSize: 40, letterSpacing: "-.015em", margin: "0 0 6px" }}>Programação</h1>
        <p style={{ fontSize: 15, color: "var(--cm2)", margin: "0 0 26px" }} aria-live="polite">
          <strong style={{ color: "var(--ct)", fontWeight: 700 }}>{filtered.length} eventos</strong>
          {summary} · fonte oficial: Sala São Paulo
        </p>

        {isLoading ? (
          <SkeletonGrid count={6} />
        ) : isError ? (
          <ErrorState onRetry={() => void refetch()} />
        ) : filtered.length === 0 ? (
          <EmptyState onClear={clear} />
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 18 }}>
            {filtered.map((vm) => (
              <EventCard key={vm.id} vm={vm} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
