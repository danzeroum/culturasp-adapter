import { useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { toEventVM } from "../lib/adapter";
import { AccessibilityIcon, AudioIcon, LibrasIcon, WheelchairIcon } from "../lib/icons";
import { useAccessibility } from "../lib/queries";
import type { AccessibilityFeature } from "../lib/types";
import { EventCard } from "../components/EventCard";
import { EmptyState, ErrorState, SkeletonGrid } from "../components/states";

const FEATURES: {
  key: AccessibilityFeature;
  label: string;
  icon: React.ReactNode;
  desc: string;
}[] = [
  { key: "libras", label: "Libras", icon: <LibrasIcon size={20} />, desc: "Língua Brasileira de Sinais — intérprete durante o evento." },
  { key: "audio_description", label: "Audiodescrição", icon: <AudioIcon size={20} />, desc: "Narração descritiva da cena para pessoas com deficiência visual." },
  { key: "wheelchair", label: "Cadeirante", icon: <WheelchairIcon size={20} />, desc: "Assentos reservados e acesso para pessoas em cadeira de rodas." },
];

function isFeature(v: string | null): v is AccessibilityFeature {
  return v === "libras" || v === "audio_description" || v === "wheelchair";
}

export function Accessibility() {
  const [params, setParams] = useSearchParams();
  const featureParam = params.get("feature");
  const feature: AccessibilityFeature = isFeature(featureParam) ? featureParam : "libras";
  const current = FEATURES.find((f) => f.key === feature)!;
  const refs = useRef<(HTMLButtonElement | null)[]>([]);

  const select = (key: AccessibilityFeature) => {
    const next = new URLSearchParams(params);
    next.set("feature", key);
    setParams(next, { replace: true });
  };

  const onKey = (e: React.KeyboardEvent, idx: number) => {
    if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      e.preventDefault();
      const n = (idx + 1) % FEATURES.length;
      refs.current[n]?.focus();
      select(FEATURES[n].key);
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      e.preventDefault();
      const n = (idx - 1 + FEATURES.length) % FEATURES.length;
      refs.current[n]?.focus();
      select(FEATURES[n].key);
    }
  };

  const { data, isLoading, isError, refetch } = useAccessibility(feature);
  const vms = (data ?? []).map(toEventVM);

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 8 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
        <span style={{ width: 40, height: 40, borderRadius: 10, background: "var(--teal)", color: "#fff", display: "grid", placeItems: "center" }}>
          <AccessibilityIcon size={22} />
        </span>
        <h1 style={{ fontSize: 40, letterSpacing: "-.015em", margin: 0 }}>Acessibilidade</h1>
      </div>
      <p style={{ fontSize: 18, color: "var(--cm)", margin: "0 0 24px", maxWidth: 640, lineHeight: 1.5 }}>
        Encontre eventos pelo recurso de que você precisa. As informações vêm da fonte oficial.
      </p>

      {/* Seletor de recurso (radiogroup) */}
      <div role="radiogroup" aria-label="Recurso de acessibilidade" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 18 }}>
        {FEATURES.map((f, idx) => {
          const active = f.key === feature;
          return (
            <button
              key={f.key}
              ref={(el) => {
                refs.current[idx] = el;
              }}
              type="button"
              role="radio"
              aria-checked={active}
              tabIndex={active ? 0 : -1}
              onClick={() => select(f.key)}
              onKeyDown={(e) => onKey(e, idx)}
              style={{
                all: "unset",
                cursor: "pointer",
                boxSizing: "border-box",
                minHeight: 56,
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "14px 16px",
                borderRadius: 12,
                border: `1.5px solid ${active ? "var(--teal-bd)" : "var(--cl2)"}`,
                background: active ? "var(--teal-bg)" : "var(--cs)",
                color: active ? "var(--teal-tx)" : "var(--ct)",
                fontWeight: 600,
                fontSize: 15.5,
              }}
            >
              <span style={{ color: active ? "var(--teal)" : "var(--cm2)", display: "inline-flex" }}>{f.icon}</span>
              {f.label}
            </button>
          );
        })}
      </div>

      {/* Painel explicativo */}
      <div style={{ background: "var(--teal-bg)", border: "1px solid var(--teal-bd)", borderRadius: 12, padding: "16px 18px", marginBottom: 26, color: "var(--teal-tx)", fontSize: 14.5, lineHeight: 1.5 }}>
        <strong>{current.label}:</strong> {current.desc}
      </div>

      <p style={{ fontSize: 15, color: "var(--cm2)", margin: "0 0 18px" }} aria-live="polite">
        <strong style={{ color: "var(--ct)", fontWeight: 700 }}>{vms.length} eventos</strong> com {current.label.toLowerCase()}
      </p>

      {isLoading ? (
        <SkeletonGrid count={3} />
      ) : isError ? (
        <ErrorState onRetry={() => void refetch()} />
      ) : vms.length === 0 ? (
        <EmptyState />
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 18 }}>
          {vms.map((vm) => (
            <EventCard key={vm.id} vm={vm} />
          ))}
        </div>
      )}
    </div>
  );
}
