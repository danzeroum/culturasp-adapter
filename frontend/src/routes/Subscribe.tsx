import { useToast } from "../app/toast";
import { api } from "../lib/api";
import { CalendarIcon, RssIcon } from "../lib/icons";

function absolute(path: string): string {
  try {
    return new URL(path, window.location.origin).href;
  } catch {
    return path;
  }
}

function FeedCard({
  icon,
  title,
  desc,
  url,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
  url: string;
}) {
  const toast = useToast();
  const copy = () => {
    navigator.clipboard?.writeText(url).catch(() => undefined);
    toast("URL copiada");
  };
  return (
    <div style={{ background: "var(--cs)", border: "1px solid var(--cl)", borderRadius: 14, padding: 22, display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ color: "var(--teal)", display: "inline-flex" }}>{icon}</span>
        <h2 style={{ fontSize: 20, margin: 0 }}>{title}</h2>
      </div>
      <p style={{ fontSize: 14.5, color: "var(--cm)", margin: 0, lineHeight: 1.5 }}>{desc}</p>
      <div style={{ display: "flex", gap: 8, alignItems: "stretch" }}>
        <input
          className="mono"
          readOnly
          value={url}
          aria-label={`URL do feed ${title}`}
          onFocus={(e) => e.currentTarget.select()}
          style={{ flex: 1, minWidth: 0, fontSize: 13, padding: "10px 12px", borderRadius: 9, border: "1px solid var(--cl2)", background: "var(--cb)", color: "var(--ct2)" }}
        />
        <button type="button" onClick={copy} className="btn btn--pill" style={{ minHeight: 0, padding: "10px 16px" }}>
          Copiar
        </button>
      </div>
    </div>
  );
}

export function Subscribe() {
  const ics = absolute(api.icsUrl());
  const rss = absolute(api.rssUrl());
  const googleUrl = `https://calendar.google.com/calendar/r?cid=${encodeURIComponent(ics)}`;
  const webcal = ics.replace(/^https?:/, "webcal:");

  return (
    <div className="container container--narrow" style={{ paddingTop: 40, paddingBottom: 8 }}>
      <h1 style={{ fontSize: 40, letterSpacing: "-.015em", margin: "0 0 10px" }}>Assinar a agenda</h1>
      <p style={{ fontSize: 18, color: "var(--cm)", margin: "0 0 28px", maxWidth: 620, lineHeight: 1.5 }}>
        Leve a programação para o seu calendário ou leitor de feeds. Os dados são abertos e
        atualizados automaticamente.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginBottom: 26 }}>
        <FeedCard
          icon={<CalendarIcon size={20} />}
          title="iCal"
          desc="Assine no seu app de calendário (Google, Apple, Outlook). Atualiza sozinho."
          url={ics}
        />
        <FeedCard
          icon={<RssIcon size={20} />}
          title="RSS"
          desc="Receba os próximos eventos no seu leitor de feeds favorito."
          url={rss}
        />
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        <a href={googleUrl} target="_blank" rel="noopener noreferrer" className="btn btn--secondary">
          Adicionar ao Google Calendar ↗
        </a>
        <a href={webcal} className="btn btn--secondary">
          Adicionar ao Apple Calendar
        </a>
      </div>

      <p style={{ fontSize: 13.5, color: "var(--cf)", marginTop: 22 }}>
        Em breve: widget incorporável para sites e portais culturais.
      </p>
    </div>
  );
}
