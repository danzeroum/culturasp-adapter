import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useHealth, useMetrics, useSampleJsonLd, useSources } from "../lib/queries";

const ENDPOINTS: { method: string; path: string; desc: string }[] = [
  { method: "GET", path: "/v1/events", desc: "lista + filtros" },
  { method: "GET", path: "/v1/events/{id}", desc: "detalhe" },
  { method: "GET", path: "/v1/events/{id}/jsonld", desc: "schema.org" },
  { method: "GET", path: "/v1/accessibility", desc: "por recurso" },
  { method: "GET", path: "/v1/events.ics · .rss", desc: "feeds" },
  { method: "GET", path: "/v1/sources", desc: "fontes" },
  { method: "GET", path: "/health · /metrics", desc: "status" },
];

// Display names for known source slugs (the API returns slugs).
const SOURCE_NAMES: Record<string, string> = { "sala-sp": "Sala São Paulo" };

const panel = { background: "#16302F", borderRadius: 13, padding: "20px 22px" } as const;

function GetBadge() {
  return (
    <span style={{ fontSize: 11, fontWeight: 800, color: "var(--free-tx)", background: "var(--free-bg)", padding: "3px 8px", borderRadius: 5 }}>
      GET
    </span>
  );
}

export function DevPortal() {
  const sources = useSources();
  const metrics = useMetrics();
  const health = useHealth();
  const jsonld = useSampleJsonLd();
  const base = api.displayBase();

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 8 }}>
      {/* B1 */}
      <span style={{ display: "inline-block", fontSize: 12, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--navacc)", marginBottom: 14 }}>
        Dados abertos · Licença MIT
      </span>
      <h1 style={{ fontSize: 48, letterSpacing: "-.02em", margin: "0 0 14px" }}>API &amp; Dados Abertos</h1>
      <p style={{ fontSize: 19, color: "var(--cm)", margin: "0 0 24px", maxWidth: 680, lineHeight: 1.5 }}>
        Toda a programação é exposta por uma API REST <strong>read-only</strong>, em JSON e
        JSON-LD (schema.org). Use livremente — atribua a fonte.
      </p>

      <div style={{ ...panel, marginBottom: 36, maxWidth: 760 }}>
        <div style={{ fontSize: 11.5, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase", color: "#7FB3AD", marginBottom: 10 }}>
          Exemplo · próximos eventos acessíveis
        </div>
        <code className="mono" style={{ display: "block", fontSize: 13.5, lineHeight: 1.7, color: "#EAF3F1", wordBreak: "break-all" }}>
          <span style={{ color: "#7FD0A0" }}>curl</span> {base}/v1/events?accessible=<span style={{ color: "#F2C57C" }}>true</span>&amp;limit=<span style={{ color: "#F2C57C" }}>5</span>
        </code>
      </div>

      {/* B2 + B3 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28, marginBottom: 36, alignItems: "start" }}>
        <div>
          <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 14 }}>
            <h2 style={{ fontSize: 22 }}>Referência da API</h2>
            <a href={api.docsUrl()} target="_blank" rel="noopener noreferrer" style={{ fontSize: 14, fontWeight: 600, color: "var(--brand)" }}>
              Abrir Swagger ↗
            </a>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
            {ENDPOINTS.map((e) => (
              <div key={e.path} style={{ display: "flex", alignItems: "center", gap: 12, background: "var(--cs)", border: "1px solid var(--cl)", borderRadius: 9, padding: "12px 15px" }}>
                <GetBadge />
                <code className="mono" style={{ fontSize: 13.5, color: "var(--ct)", flex: 1 }}>{e.path}</code>
                <span style={{ fontSize: 12.5, color: "var(--cf)" }}>{e.desc}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 style={{ fontSize: 22, marginBottom: 14 }}>Resposta JSON-LD</h2>
          <div style={{ ...panel, background: "#1C1814", minHeight: 120 }}>
            <pre className="mono" style={{ margin: 0, fontSize: 12.5, lineHeight: 1.6, color: "#EAF3F1", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {jsonld.isLoading
                ? "carregando…"
                : jsonld.data
                  ? JSON.stringify(jsonld.data, null, 2)
                  : "// nenhum evento disponível ainda"}
            </pre>
          </div>
          <p style={{ fontSize: 13, color: "var(--cf)", marginTop: 10 }}>
            Cada evento também está disponível como <code className="mono">schema.org/Event</code>{" "}
            em <code className="mono">/v1/events/&#123;id&#125;/jsonld</code>.
          </p>
        </div>
      </div>

      {/* B4 — Fontes & cobertura */}
      <h2 style={{ fontSize: 26, margin: "0 0 16px" }}>Fontes &amp; cobertura</h2>
      <div style={{ background: "var(--cs)", border: "1px solid var(--cl)", borderRadius: 13, overflow: "hidden", marginBottom: 16 }}>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1.4fr 1fr", padding: "14px 22px", background: "var(--csoft)", fontSize: 12, fontWeight: 800, letterSpacing: ".05em", textTransform: "uppercase", color: "var(--cm2)" }}>
          <span>Fonte</span>
          <span>Status</span>
          <span>Assinatura de layout</span>
          <span>Última coleta</span>
        </div>
        {sources.isLoading ? (
          <div style={{ padding: "18px 22px", color: "var(--cm)" }}>carregando…</div>
        ) : sources.isError ? (
          <div style={{ padding: "18px 22px", color: "var(--weekend-tx)" }} role="alert">
            não foi possível carregar as fontes
          </div>
        ) : (
          (sources.data ?? []).map((s) => (
            <div key={s.source} style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1.4fr 1fr", padding: "18px 22px", borderTop: "1px solid var(--csoft)", alignItems: "center" }}>
              <span style={{ fontSize: 15, fontWeight: 600, color: "var(--ct)" }}>{SOURCE_NAMES[s.source] ?? s.source}</span>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 7, fontSize: 13.5, fontWeight: 600, color: "var(--free-tx)" }}>
                <span style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--free-dot)" }} />
                Ativo
              </span>
              <span style={{ fontSize: 13.5, color: "var(--cm)" }}>{s.layout_signature ? "Estável" : "—"}</span>
              <span style={{ fontSize: 13.5, color: "var(--cf)" }} title="não exposta pela API">—</span>
            </div>
          ))
        )}
      </div>
      <p style={{ fontSize: 13, color: "var(--cf)", marginBottom: 28, maxWidth: 720, lineHeight: 1.5 }}>
        Fontes <strong>experimentais</strong> (ex.: Pinacoteca) estão em validação e ainda não
        são servidas pela API. A data da última coleta não é exposta publicamente.
      </p>

      {/* B5 — status */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 11, background: health.data ? "var(--free-bg)" : "var(--csoft)", border: `1px solid ${health.data ? "var(--free-bd)" : "var(--cl2)"}`, borderRadius: 11, padding: "14px 20px" }}>
          <span style={{ width: 10, height: 10, borderRadius: "50%", background: health.data ? "var(--free-dot)" : "var(--cf)" }} />
          <span style={{ fontSize: 14, fontWeight: 700, color: health.data ? "var(--free-tx)" : "var(--cm)" }}>
            /health · {health.isLoading ? "verificando…" : health.data ? "No ar" : "indisponível"}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 11, background: "var(--cs)", border: "1px solid var(--cl2)", borderRadius: 11, padding: "14px 20px" }}>
          <span style={{ fontSize: 14, fontWeight: 600, color: "var(--cm)" }}>
            /metrics · {metrics.data ? `${metrics.data.events_total} eventos · ${metrics.data.sources.length} fontes` : "—"}
          </span>
        </div>
      </div>

      <p style={{ marginTop: 22 }}>
        <Link to="/kit" style={{ fontSize: 14, fontWeight: 600, color: "var(--brand)" }}>
          Kit de componentes &amp; ícones →
        </Link>
      </p>
    </div>
  );
}
