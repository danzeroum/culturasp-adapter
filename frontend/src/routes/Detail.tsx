import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useToast } from "../app/toast";
import { makeICS, toEventVM } from "../lib/adapter";
import { api } from "../lib/api";
import { ApiError } from "../lib/api";
import {
  AccessibilityIcon,
  AudioIcon,
  CalendarIcon,
  CheckIcon,
  CodeIcon,
  ExternalIcon,
  InfoIcon,
  LibrasIcon,
  ShareIcon,
  WheelchairIcon,
} from "../lib/icons";
import { useEvent } from "../lib/queries";
import { LeaveModal } from "../components/LeaveModal";
import { ErrorState } from "../components/states";
import type { CulturalEvent } from "../lib/types";

const card = { background: "var(--cs)", border: "1px solid var(--cl)", borderRadius: 12, padding: 20 } as const;
const cardLabel = { fontSize: 12, fontWeight: 800, letterSpacing: ".07em", textTransform: "uppercase", color: "var(--cf)", marginBottom: 10 } as const;

function AccessRow({
  icon,
  available,
  title,
  text,
  status,
  forceTeal,
}: {
  icon: React.ReactNode;
  available: boolean;
  title: string;
  text: string;
  status: string;
  forceTeal?: boolean;
}) {
  const boxBg = forceTeal ? "#0C7C84" : available ? "#D2EBEC" : "#EFEBE2";
  const boxFg = forceTeal ? "#fff" : available ? "#0A5B61" : "#9A9486";
  const statusColor = available || forceTeal ? "#0A5B61" : "#9A9486";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, background: "#FCFCFD", border: "1px solid #CFE7E8", borderRadius: 10, padding: "14px 16px" }}>
      <span style={{ width: 38, height: 38, flex: "none", borderRadius: 9, background: boxBg, color: boxFg, display: "grid", placeItems: "center" }}>
        {icon}
      </span>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 15.5, fontWeight: 700, color: "#1B1712" }}>{title}</div>
        <div style={{ fontSize: 13.5, color: "#544C40" }}>{text}</div>
      </div>
      <span style={{ fontSize: 13, fontWeight: 700, color: statusColor }}>{status}</span>
    </div>
  );
}

export function Detail() {
  const { id } = useParams<{ id: string }>();
  const toast = useToast();
  const { data, isLoading, isError, error, refetch } = useEvent(id);
  const [leaving, setLeaving] = useState<{ name: string; url: string } | null>(null);

  if (isLoading) {
    return (
      <div className="container container--detail" style={{ paddingTop: 36 }}>
        <div className="shimmer" style={{ height: 28, width: 120, marginBottom: 20 }} />
        <div className="shimmer" style={{ height: 56, width: "70%", marginBottom: 24 }} />
        <div className="shimmer" style={{ height: 220 }} />
      </div>
    );
  }

  if (isError && error instanceof ApiError && error.status === 404) {
    return <NotFound />;
  }
  if (isError || !data) {
    return (
      <div className="container container--detail" style={{ paddingTop: 36 }}>
        <ErrorState onRetry={() => void refetch()} />
      </div>
    );
  }

  const event: CulturalEvent = data;
  const vm = toEventVM(event);

  const addToCalendar = () => {
    const blob = new Blob([makeICS(event, vm)], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${vm.id}.ics`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    toast("Evento adicionado ao calendário (.ics)");
  };

  const share = () => {
    const link = `${window.location.origin}/eventos/${encodeURIComponent(vm.id)}`;
    navigator.clipboard?.writeText(link).catch(() => undefined);
    toast("Link do evento copiado");
  };

  return (
    <div className="container container--detail" style={{ paddingTop: 28, paddingBottom: 8 }}>
      <Link to="/programacao" style={{ fontSize: 14, fontWeight: 600, color: "var(--cm)" }}>
        ← Voltar à programação
      </Link>

      <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "18px 0 10px", flexWrap: "wrap" }}>
        <span style={{ fontSize: 12, fontWeight: 700, letterSpacing: ".05em", textTransform: "uppercase", color: "#fff", background: vm.typeColor, padding: "4px 10px", borderRadius: 999 }}>
          {vm.typeLabel}
        </span>
        <a href={vm.sourceUrl} target="_blank" rel="noopener noreferrer" style={{ fontSize: 13.5, color: "var(--cm)", display: "inline-flex", alignItems: "center", gap: 5 }}>
          Fonte: {vm.source} <ExternalIcon size={13} />
        </a>
      </div>

      <h1 style={{ fontSize: 46, lineHeight: 1.06, letterSpacing: "-.015em", margin: "0 0 24px" }}>{vm.title}</h1>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 28, alignItems: "start" }}>
        {/* Coluna principal */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div style={card}>
              <div style={cardLabel}>Quando</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: "var(--ct)", lineHeight: 1.3 }}>{vm.dateFull}</div>
              {vm.timeLine && <div style={{ fontSize: 15, color: "var(--cm)", marginTop: 5 }}>{vm.timeLine}</div>}
            </div>
            <div style={card}>
              <div style={cardLabel}>Onde</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: "var(--ct)", lineHeight: 1.3 }}>{vm.venueName}</div>
            </div>
          </div>

          {/* Programa ou Sobre */}
          {vm.hasProgram ? (
            <div>
              <h2 style={{ fontSize: 25, margin: "0 0 6px" }}>Programa</h2>
              {(vm.conductor || vm.performersLine) && (
                <p style={{ fontSize: 14.5, color: "var(--cm)", margin: "0 0 16px" }}>
                  {vm.conductor && (
                    <>
                      Regência de <strong>{vm.conductor}</strong>
                    </>
                  )}
                  {vm.conductor && vm.performersLine ? " · " : ""}
                  {vm.performersLine}
                </p>
              )}
              <div style={{ background: "var(--cs)", border: "1px solid var(--cl)", borderRadius: 12, overflow: "hidden" }}>
                {vm.program.map((p, i) => (
                  <div key={i} style={{ display: "flex", gap: 18, padding: "14px 20px", borderBottom: i < vm.program.length - 1 ? "1px solid var(--csoft)" : "none" }}>
                    <span style={{ fontFamily: "'Newsreader',serif", fontSize: 16, fontWeight: 600, color: "var(--brand)", minWidth: 130 }}>{p.composer ?? "—"}</span>
                    <span style={{ fontSize: 15, color: "var(--ct)" }}>{p.work ?? ""}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {/* Acessibilidade — alto contraste fixo (claro nos dois temas) */}
          <section aria-label="Recursos de acessibilidade" style={{ background: "#EAF5F5", border: "1.5px solid #BBDFE1", borderRadius: 14, padding: 26 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 11, marginBottom: 6 }}>
              <span style={{ width: 34, height: 34, borderRadius: 9, background: "#0C7C84", color: "#fff", display: "grid", placeItems: "center" }}>
                <AccessibilityIcon size={20} />
              </span>
              <h2 style={{ fontSize: 25, margin: 0, color: "#0A4F55" }}>Acessibilidade</h2>
            </div>
            <p style={{ fontSize: 14, color: "#3C6A6E", margin: "0 0 18px" }}>
              Informações fornecidas pela fonte oficial. Em caso de dúvida, confirme na instituição.
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <AccessRow icon={<LibrasIcon size={20} />} available={vm.libras} title="Tradução em Libras" text={vm.librasText} status={vm.librasStatus} />
              <AccessRow icon={<AudioIcon size={20} />} available={vm.audio} title="Audiodescrição" text={vm.audioText} status={vm.audioStatus} />
              <AccessRow icon={<WheelchairIcon size={20} />} available={vm.hasWheel} forceTeal title="Assentos para cadeirantes" text={vm.wheelText} status={vm.wheelStatus} />
            </div>
            {vm.accNotes && <p style={{ fontSize: 13, color: "#3C6A6E", margin: "16px 0 0", lineHeight: 1.5 }}>{vm.accNotes}</p>}
          </section>

          {/* Procedência */}
          <div style={{ display: "flex", gap: 11, alignItems: "flex-start", background: "var(--prov-bg)", border: "1px solid var(--prov-bd)", borderRadius: 11, padding: "16px 18px" }}>
            <span style={{ color: "var(--prov-ic)", flex: "none", marginTop: 1, display: "inline-flex" }}>
              <InfoIcon size={18} />
            </span>
            <p style={{ fontSize: 13.5, lineHeight: 1.5, color: "var(--prov-tx)", margin: 0 }}>
              Dados coletados de <strong>{vm.source}</strong>
              {vm.scrapedAtLabel ? ` em ${vm.scrapedAtLabel}` : ""}. O CulturaSP é um portal de dados
              abertos e <strong>não vende ingressos</strong> — sempre confirme horários e
              disponibilidade no site oficial.
            </p>
          </div>
        </div>

        {/* Aside */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14, position: "sticky", top: 90 }}>
          <div style={{ background: "var(--cs)", border: "1px solid var(--cl)", borderRadius: 14, padding: 24, boxShadow: "0 18px 40px -28px rgba(27,23,18,.35)" }}>
            {vm.free && (
              <div style={{ display: "inline-flex", alignItems: "center", gap: 7, fontSize: 14, fontWeight: 800, color: "var(--free-tx)", background: "var(--free-bg)", border: "1px solid var(--free-bd)", padding: "7px 14px", borderRadius: 999, marginBottom: 16 }}>
                <CheckIcon size={15} /> Entrada gratuita
              </div>
            )}
            <div style={{ fontSize: 13, fontWeight: 700, color: "var(--cm)", marginBottom: 5 }}>Retirada de ingressos</div>
            <p style={{ fontSize: 14.5, lineHeight: 1.5, color: "var(--ct)", margin: "0 0 4px" }}>
              {vm.ticketDist || "Informação não disponível — confira no site oficial."}
            </p>
            {vm.ticketCancel && <p style={{ fontSize: 13, lineHeight: 1.5, color: "var(--cm2)", margin: "0 0 20px" }}>{vm.ticketCancel}</p>}

            {vm.externalUrl ? (
              <>
                <button type="button" onClick={() => setLeaving({ name: vm.source, url: vm.externalUrl! })} className="btn btn--primary" style={{ width: "100%" }}>
                  Retirar no site oficial
                  <ExternalIcon size={17} />
                </button>
                <p style={{ fontSize: 12, color: "var(--cf)", textAlign: "center", margin: "9px 0 0" }}>
                  Abre o site da {vm.source} em nova aba.
                </p>
              </>
            ) : (
              <a href={vm.sourceUrl} target="_blank" rel="noopener noreferrer" className="btn btn--secondary" style={{ width: "100%" }}>
                Ver no site oficial <ExternalIcon size={16} />
              </a>
            )}
          </div>

          <div style={{ background: "var(--cs)", border: "1px solid var(--cl)", borderRadius: 14, padding: 10, display: "flex", flexDirection: "column", gap: 2 }}>
            <button type="button" onClick={addToCalendar} style={asideBtn}>
              <span style={{ color: "var(--teal)", display: "inline-flex" }}>
                <CalendarIcon size={18} />
              </span>
              Adicionar ao calendário
            </button>
            <button type="button" onClick={share} style={asideBtn}>
              <span style={{ color: "var(--teal)", display: "inline-flex" }}>
                <ShareIcon size={18} />
              </span>
              Compartilhar
            </button>
            <a href={api.jsonLdUrl(vm.id)} target="_blank" rel="noopener noreferrer" style={{ ...asideBtn, color: "var(--cf)", fontSize: 13.5, textDecoration: "none" }}>
              <CodeIcon size={18} />
              Ver JSON-LD (dev)
            </a>
          </div>
        </div>
      </div>

      {leaving && <LeaveModal name={leaving.name} url={leaving.url} onCancel={() => setLeaving(null)} />}
    </div>
  );
}

const asideBtn = {
  all: "unset",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  gap: 12,
  padding: "12px 14px",
  borderRadius: 9,
  fontSize: 14.5,
  fontWeight: 600,
  color: "var(--ct)",
  minHeight: 44,
  boxSizing: "border-box",
} as const;

export function NotFound() {
  return (
    <div className="container" style={{ paddingTop: 80, paddingBottom: 80, textAlign: "center" }}>
      <div style={{ fontFamily: "'Newsreader',serif", fontSize: 54, color: "var(--brand)", fontWeight: 600 }}>404</div>
      <h1 style={{ fontSize: 28, margin: "8px 0 6px" }}>Evento não encontrado</h1>
      <p style={{ fontSize: 16, color: "var(--cm)", margin: "0 0 20px" }}>
        Ele pode ter saído de cartaz ou o endereço está incorreto.
      </p>
      <Link to="/" className="btn btn--primary">
        Voltar ao início
      </Link>
    </div>
  );
}
