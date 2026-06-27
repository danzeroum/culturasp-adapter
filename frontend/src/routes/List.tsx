import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { toEventVM, type EventVM } from "../lib/adapter";
import { fmt, t } from "../lib/i18n";
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

interface FilterState {
  accessible: boolean;
  weekend: boolean;
  free: boolean;
  tipo: string[];
  setFlag: (key: string, on: boolean) => void;
  toggleTipo: (t: string) => void;
  clear: () => void;
}

/** Filter controls, shared between the desktop sidebar and the mobile sheet. */
function FilterControls({ s }: { s: FilterState }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: 13, fontWeight: 800, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--ct)" }}>
          {t.list.filters}
        </span>
        <button type="button" onClick={s.clear} style={{ all: "unset", cursor: "pointer", fontSize: 13, fontWeight: 600, color: "var(--brand)" }}>
          {t.list.clear}
        </button>
      </div>

      <div>
        <div style={{ fontSize: 13, fontWeight: 700, color: "var(--cm)", marginBottom: 11 }}>{t.list.periodo}</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
          <button
            type="button"
            aria-pressed={s.weekend}
            onClick={() => s.setFlag("weekend", !s.weekend)}
            style={{
              all: "unset",
              cursor: "pointer",
              fontSize: 13,
              fontWeight: 600,
              padding: "7px 12px",
              borderRadius: 8,
              border: `1px solid ${s.weekend ? "var(--weekend-bd)" : "var(--cl2)"}`,
              color: s.weekend ? "var(--weekend-tx)" : "var(--cm2)",
              background: s.weekend ? "var(--weekend-bg)" : "var(--cb)",
            }}
          >
            {t.list.weekend}
          </button>
        </div>
      </div>

      {divider}

      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 13, fontWeight: 700, color: "var(--navacc)", marginBottom: 11 }}>
          <AccessibilityIcon size={15} />
          {t.list.a11yGroup}
        </div>
        <Switch checked={s.accessible} onChange={() => s.setFlag("accessible", !s.accessible)} label={t.list.a11ySwitch} />
        <p style={{ fontSize: 12, color: "var(--cf)", margin: "8px 2px 0", lineHeight: 1.4 }}>{t.list.a11yHint}</p>
      </div>

      {divider}

      <div>
        <div style={{ fontSize: 13, fontWeight: 700, color: "var(--cm)", marginBottom: 11 }}>{t.list.tipo}</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
          {[t.list.tipoConcerto, t.list.tipoExposicao].map((label) => (
            <label key={label} style={{ display: "flex", alignItems: "center", gap: 9, fontSize: 14, color: "var(--ct)", cursor: "pointer", minHeight: 28 }}>
              <input type="checkbox" checked={s.tipo.includes(label)} onChange={() => s.toggleTipo(label)} />
              {label}
            </label>
          ))}
        </div>
      </div>

      {divider}

      <Switch checked={s.free} onChange={() => s.setFlag("free", !s.free)} label={t.list.onlyFree} />
    </div>
  );
}

/** Mobile-only bottom sheet wrapping the same filter controls. */
function FilterSheet({ s, onClose }: { s: FilterState; onClose: () => void }) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    // Backdrop. Keyboard users dismiss via Escape (handled above) or the close
    // button; click-to-dismiss here is a supplementary mouse affordance.
    // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions
    <div
      className="sheet-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="sheet" role="dialog" aria-modal="true" aria-label={t.list.filters}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
          <span style={{ fontSize: 16, fontWeight: 800, color: "var(--ct)" }}>{t.list.filters}</span>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label={t.list.filtersClose}
            className="btn btn--secondary"
            style={{ minHeight: 40, padding: "8px 14px" }}
          >
            {t.list.filtersClose}
          </button>
        </div>
        <FilterControls s={s} />
      </div>
    </div>
  );
}

export function List() {
  const [params, setParams] = useSearchParams();
  const [sheetOpen, setSheetOpen] = useState(false);
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
  const toggleTipo = (label: string) => {
    const next = new URLSearchParams(params);
    const current = next.getAll("tipo");
    next.delete("tipo");
    const updated = current.includes(label) ? current.filter((x) => x !== label) : [...current, label];
    updated.forEach((x) => next.append("tipo", x));
    setParams(next, { replace: true });
  };
  const clear = () => setParams(new URLSearchParams(), { replace: true });

  const filterState: FilterState = { accessible, weekend, free, tipo, setFlag, toggleTipo, clear };

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

  const activeCount = [accessible, weekend, free].filter(Boolean).length + tipo.length;
  const activeBits = [
    accessible && t.list.bitAccessible,
    weekend && t.list.bitWeekend,
    free && t.list.bitFree,
    ...tipo.map((x) => x.toLowerCase()),
  ].filter(Boolean);
  const summary = activeBits.length ? ` · ${activeBits.join(", ")}` : "";

  return (
    <div className="container list-layout" style={{ paddingTop: 36, paddingBottom: 8 }}>
      {/* Filtros — sidebar no desktop */}
      <aside
        className="filters-aside"
        aria-label={t.list.filters}
        style={{
          position: "sticky",
          top: 90,
          background: "var(--cs)",
          border: "1px solid var(--cl)",
          borderRadius: 12,
          padding: 22,
        }}
      >
        <FilterControls s={filterState} />
      </aside>

      {/* Resultados */}
      <div>
        <h1 style={{ fontSize: 40, letterSpacing: "-.015em", margin: "0 0 6px" }}>{t.list.title}</h1>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, marginBottom: 26 }}>
          <p style={{ fontSize: 15, color: "var(--cm2)", margin: 0 }} aria-live="polite">
            <strong style={{ color: "var(--ct)", fontWeight: 700 }}>{fmt(t.list.summaryCount, { count: filtered.length })}</strong>
            {summary} · {t.list.summarySource}
          </p>
          {/* Botão de filtros — só no mobile (CSS) */}
          <button
            type="button"
            className="btn btn--secondary filter-fab"
            onClick={() => setSheetOpen(true)}
            aria-haspopup="dialog"
            style={{ minHeight: 40, padding: "8px 14px", fontSize: 14 }}
          >
            {t.list.filtersOpen}
            {activeCount > 0 && (
              <span aria-hidden="true" style={{ marginLeft: 7, background: "var(--brand)", color: "#fff", borderRadius: 999, fontSize: 12, fontWeight: 800, padding: "1px 7px" }}>
                {activeCount}
              </span>
            )}
          </button>
        </div>

        {isLoading ? (
          <SkeletonGrid count={6} />
        ) : isError ? (
          <ErrorState onRetry={() => void refetch()} />
        ) : filtered.length === 0 ? (
          <EmptyState onClear={clear} />
        ) : (
          <div className="card-grid">
            {filtered.map((vm) => (
              <EventCard key={vm.id} vm={vm} />
            ))}
          </div>
        )}
      </div>

      {sheetOpen && <FilterSheet s={filterState} onClose={() => setSheetOpen(false)} />}
    </div>
  );
}
