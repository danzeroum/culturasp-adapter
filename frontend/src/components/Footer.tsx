import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer style={{ borderTop: "1px solid var(--cl)", marginTop: 64, background: "var(--cb)" }}>
      <div
        className="container"
        style={{
          padding: "28px 40px",
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          justifyContent: "space-between",
          alignItems: "center",
          color: "var(--cm2)",
          fontSize: 13.5,
        }}
      >
        <span>
          CulturaSP · portal de dados culturais abertos. Não vende ingressos — sempre confirme na
          fonte oficial.
        </span>
        <nav aria-label="Rodapé" style={{ display: "flex", gap: 16 }}>
          <Link to="/dev" style={{ color: "var(--cm)" }}>
            Dados abertos
          </Link>
          <a
            href="https://github.com/danzeroum/culturasp-adapter"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "var(--cm)" }}
          >
            Repositório ↗
          </a>
        </nav>
      </div>
    </footer>
  );
}
