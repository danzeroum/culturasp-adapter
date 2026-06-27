import { NavLink } from "react-router-dom";
import { useTheme } from "../app/theme";
import { AccessibilityIcon, MoonIcon, SunIcon } from "../lib/icons";
import { t } from "../lib/i18n";

const navStyle = ({ isActive }: { isActive: boolean }) => ({
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "8px 12px",
  borderRadius: 8,
  fontSize: 14.5,
  fontWeight: 600,
  textDecoration: "none",
  color: isActive ? "var(--ct)" : "var(--cm)",
  background: isActive ? "var(--csoft)" : "transparent",
});

export function Header() {
  const { theme, toggle } = useTheme();
  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        background: "color-mix(in srgb, var(--cb) 88%, transparent)",
        backdropFilter: "blur(6px)",
        borderBottom: "1px solid var(--cl)",
      }}
    >
      <div
        className="container"
        style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 40px" }}
      >
        <NavLink to="/" style={{ display: "flex", alignItems: "center", gap: 11, textDecoration: "none" }}>
          <span
            aria-hidden="true"
            style={{
              width: 30,
              height: 30,
              borderRadius: 8,
              background: "var(--brand)",
              color: "#fff",
              display: "grid",
              placeItems: "center",
              fontFamily: "'Newsreader',serif",
              fontWeight: 600,
              fontSize: 19,
            }}
          >
            C
          </span>
          <span style={{ fontSize: 22, fontWeight: 700, color: "var(--ct)" }}>{t.app.name}</span>
        </NavLink>

        <nav aria-label={t.nav.label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <NavLink to="/programacao" style={navStyle}>
            {t.nav.programacao}
          </NavLink>
          <NavLink to="/acessibilidade" style={({ isActive }) => ({ ...navStyle({ isActive }), color: isActive ? "var(--navacc)" : "var(--navacc)" })}>
            <AccessibilityIcon size={15} />
            {t.nav.acessibilidade}
          </NavLink>
          <NavLink to="/dev" style={navStyle}>
            {t.nav.dadosAbertos}
          </NavLink>
          <button
            type="button"
            onClick={toggle}
            aria-label={theme === "dark" ? t.nav.themeToLight : t.nav.themeToDark}
            aria-pressed={theme === "dark"}
            style={{
              all: "unset",
              cursor: "pointer",
              width: 38,
              height: 38,
              borderRadius: 9,
              display: "grid",
              placeItems: "center",
              color: "var(--ct)",
              marginLeft: 4,
            }}
          >
            {theme === "dark" ? <MoonIcon size={18} /> : <SunIcon size={18} />}
          </button>
        </nav>
      </div>
    </header>
  );
}
