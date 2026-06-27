import { Link, useNavigate } from "react-router-dom";
import { toEventVM } from "../lib/adapter";
import { SearchIcon } from "../lib/icons";
import { useEvents } from "../lib/queries";
import { EventCard } from "../components/EventCard";
import { ErrorState, SkeletonGrid } from "../components/states";

const chip = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "9px 15px",
  borderRadius: 999,
  border: "1px solid var(--cl2)",
  background: "var(--cs)",
  color: "var(--ct2)",
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
  textDecoration: "none",
} as const;

export function Home() {
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = useEvents({ limit: 8 });
  const vms = (data ?? [])
    .slice()
    .sort((a, b) => (a.start ?? "").localeCompare(b.start ?? ""))
    .map(toEventVM)
    .slice(0, 4);

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 8 }}>
      {/* Hero */}
      <section style={{ maxWidth: 760, marginBottom: 40 }}>
        <span
          style={{
            display: "inline-block",
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: ".08em",
            textTransform: "uppercase",
            color: "var(--navacc)",
            marginBottom: 14,
          }}
        >
          Dados culturais abertos · São Paulo
        </span>
        <h1 style={{ fontSize: 60, lineHeight: 1.02, letterSpacing: "-.02em", margin: "0 0 16px" }}>
          A programação cultural de SP, acessível a todos.
        </h1>
        <p style={{ fontSize: 19, color: "var(--cm)", margin: "0 0 22px", lineHeight: 1.5 }}>
          Descubra concertos e exposições, filtre por recursos de acessibilidade e seja levado ao
          canal oficial para retirar seu ingresso.
        </p>
        <form
          role="search"
          onSubmit={(e) => {
            e.preventDefault();
            navigate("/programacao");
          }}
          style={{ display: "flex", gap: 10, alignItems: "center" }}
        >
          <span style={{ position: "relative", flex: 1, display: "flex", alignItems: "center" }}>
            <span style={{ position: "absolute", left: 14, color: "var(--cf)", display: "inline-flex" }}>
              <SearchIcon size={20} />
            </span>
            <input
              type="search"
              aria-label="Buscar eventos"
              placeholder="Buscar por evento, artista ou local…"
              style={{
                width: "100%",
                padding: "14px 16px 14px 44px",
                borderRadius: 10,
                border: "1px solid var(--cl2)",
                background: "var(--cs)",
                color: "var(--ct)",
                fontSize: 16,
              }}
            />
          </span>
          <button type="submit" className="btn btn--pill">
            Explorar
          </button>
        </form>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 9, marginTop: 16 }}>
          <Link to="/programacao?accessible=true" style={chip}>
            Acessível
          </Link>
          <Link to="/programacao?weekend=true" style={chip}>
            Este fim de semana
          </Link>
          <Link to="/programacao?free=true" style={chip}>
            Gratuito
          </Link>
        </div>
      </section>

      {/* Próximos eventos */}
      <section aria-labelledby="prox" style={{ marginBottom: 40 }}>
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 18 }}>
          <h2 id="prox" style={{ fontSize: 28 }}>
            Próximos eventos
          </h2>
          <Link to="/programacao" style={{ fontSize: 15, fontWeight: 600, color: "var(--brand)" }}>
            Ver toda a programação →
          </Link>
        </div>
        {isLoading ? (
          <SkeletonGrid count={4} />
        ) : isError ? (
          <ErrorState onRetry={() => void refetch()} />
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 18 }}>
            {vms.map((vm) => (
              <EventCard key={vm.id} vm={vm} />
            ))}
          </div>
        )}
      </section>

      {/* Assinar */}
      <section
        style={{
          background: "var(--dark-band)",
          color: "var(--dark-band-tx)",
          borderRadius: 16,
          padding: "28px 32px",
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <h2 style={{ color: "var(--dark-band-tx)", fontSize: 24, margin: "0 0 4px" }}>
            Leve a agenda com você
          </h2>
          <p style={{ color: "var(--dark-band-tx2)", margin: 0, fontSize: 15 }}>
            Assine o feed iCal/RSS ou adicione ao seu calendário.
          </p>
        </div>
        <Link to="/assinar" className="btn btn--primary">
          Assinar agenda
        </Link>
      </section>
    </div>
  );
}
