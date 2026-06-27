import { Link } from "react-router-dom";
import { t } from "../lib/i18n";

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
        <span>{t.footer.blurb}</span>
        <nav aria-label={t.footer.label} style={{ display: "flex", gap: 16 }}>
          <Link to="/dev" style={{ color: "var(--cm)" }}>
            {t.footer.dadosAbertos}
          </Link>
          <a
            href={t.footer.repoUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "var(--cm)" }}
          >
            {t.footer.repo}
          </a>
        </nav>
      </div>
    </footer>
  );
}
