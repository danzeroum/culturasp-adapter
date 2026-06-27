import { EmptySearchIcon, InfoIcon } from "../lib/icons";

export function CardSkeleton() {
  return (
    <div style={{ background: "var(--cs)", border: "1px solid var(--cl)", borderRadius: 6, overflow: "hidden" }}>
      <div className="shimmer" style={{ height: 96, borderRadius: 0 }} />
      <div style={{ padding: "16px 18px", display: "flex", flexDirection: "column", gap: 10 }}>
        <div className="shimmer" style={{ height: 20, width: "80%" }} />
        <div className="shimmer" style={{ height: 14, width: "55%" }} />
        <div className="shimmer" style={{ height: 22, width: 90, borderRadius: 999 }} />
      </div>
    </div>
  );
}

export function SkeletonGrid({ count = 4 }: { count?: number }) {
  return (
    <div aria-hidden="true" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 18 }}>
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

export function EmptyState({ onClear }: { onClear?: () => void }) {
  return (
    <div
      style={{
        gridColumn: "1 / -1",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        gap: 12,
        padding: "64px 30px",
        background: "var(--cs)",
        border: "1px dashed var(--cl2)",
        borderRadius: 14,
      }}
    >
      <span style={{ width: 54, height: 54, borderRadius: 14, background: "var(--csoft)", color: "var(--cm2)", display: "grid", placeItems: "center" }}>
        <EmptySearchIcon size={26} />
      </span>
      <h3 style={{ fontSize: 24, margin: "2px 0 0", color: "var(--ct)" }}>Nenhum evento com esses filtros</h3>
      <p style={{ fontSize: 15, lineHeight: 1.5, color: "var(--cm)", margin: 0, maxWidth: 360 }}>
        Tente afrouxar a busca — incluir dias de semana, eventos pagos ou outras fontes.
      </p>
      {onClear && (
        <button type="button" onClick={onClear} className="btn btn--primary" style={{ marginTop: 6 }}>
          Limpar filtros
        </button>
      )}
    </div>
  );
}

export function ErrorState({ onRetry }: { onRetry?: () => void }) {
  return (
    <div
      role="alert"
      style={{
        gridColumn: "1 / -1",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        gap: 12,
        padding: "56px 30px",
        background: "var(--cs)",
        border: "1px solid var(--cl)",
        borderRadius: 14,
      }}
    >
      <span style={{ width: 54, height: 54, borderRadius: 14, background: "var(--weekend-bg)", color: "var(--weekend-tx)", display: "grid", placeItems: "center" }}>
        <InfoIcon size={26} />
      </span>
      <h3 style={{ fontSize: 23, margin: 0, color: "var(--ct)" }}>Não foi possível carregar</h3>
      <p style={{ fontSize: 15, lineHeight: 1.5, color: "var(--cm)", margin: 0, maxWidth: 380 }}>
        Verifique sua conexão. Os dados podem estar desatualizados — confirme sempre na fonte oficial.
      </p>
      {onRetry && (
        <button type="button" onClick={onRetry} className="btn btn--primary" style={{ marginTop: 6 }}>
          Tentar de novo
        </button>
      )}
    </div>
  );
}
