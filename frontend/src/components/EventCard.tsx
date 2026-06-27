import { Link } from "react-router-dom";
import type { EventVM } from "../lib/adapter";
import { AudioIcon, CheckIcon, LibrasIcon, WheelchairIcon } from "../lib/icons";

function Chip({ children, kind }: { children: React.ReactNode; kind: "free" | "access" | "exp" }) {
  const styles =
    kind === "free"
      ? { color: "var(--free-tx)", background: "var(--free-bg)", border: "1px solid var(--free-bd)" }
      : kind === "exp"
        ? { color: "var(--exp-tx)", background: "var(--exp-bg)", border: "1px solid var(--exp-bd)" }
        : { color: "var(--teal-tx)", background: "var(--teal-bg)", border: "1px solid var(--teal-bd)" };
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        fontSize: 12,
        fontWeight: kind === "free" ? 700 : 600,
        padding: "4px 9px",
        borderRadius: 999,
        ...styles,
      }}
    >
      {children}
    </span>
  );
}

export function EventCard({ vm }: { vm: EventVM }) {
  return (
    <Link
      to={`/eventos/${encodeURIComponent(vm.id)}`}
      aria-label={vm.ariaLabel}
      className="event-card"
      style={{
        display: "flex",
        flexDirection: "column",
        background: "var(--cs)",
        border: "1px solid var(--cl)",
        borderRadius: 6,
        overflow: "hidden",
        textDecoration: "none",
        color: "inherit",
        transition: "transform .18s ease, box-shadow .18s ease, border-color .18s ease",
      }}
    >
      {/* Cover — typographic, colored by event type */}
      <div
        style={{
          padding: "16px 18px",
          minHeight: 96,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          color: "#fff",
          background: vm.typeColor,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
          <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", opacity: 0.92 }}>
            {vm.source}
          </span>
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: ".06em",
              textTransform: "uppercase",
              background: "rgba(255,255,255,.18)",
              padding: "3px 9px",
              borderRadius: 999,
            }}
          >
            {vm.typeLabel}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 8 }}>
          {vm.isRange ? (
            <span style={{ fontFamily: "'Newsreader',serif", fontSize: 26, fontWeight: 500, lineHeight: 1 }}>
              {vm.coverRange}
            </span>
          ) : vm.isSingle ? (
            <>
              <span style={{ fontFamily: "'Newsreader',serif", fontSize: 46, fontWeight: 500, lineHeight: 0.86 }}>
                {vm.coverDay}
              </span>
              <span style={{ fontSize: 13, fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", paddingBottom: 4 }}>
                {vm.coverMonth}
              </span>
            </>
          ) : (
            <span style={{ fontFamily: "'Newsreader',serif", fontSize: 22, fontWeight: 500 }}>Data a confirmar</span>
          )}
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: "14px 18px 18px", display: "flex", flexDirection: "column", gap: 10, flex: 1 }}>
        <h3 style={{ fontFamily: "'Newsreader',serif", fontWeight: 600, fontSize: 20, lineHeight: 1.16, color: "var(--ct)", letterSpacing: "-.01em" }}>
          {vm.title}
        </h3>
        <div style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 13.5, color: "var(--cm2)", fontWeight: 500 }}>
          <span>{vm.whenLabel}</span>
          <span aria-hidden="true" style={{ opacity: 0.5 }}>
            ·
          </span>
          <span>{vm.venueName}</span>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 2 }}>
          {vm.free && (
            <Chip kind="free">
              <CheckIcon size={13} /> Gratuito
            </Chip>
          )}
          {vm.libras && (
            <Chip kind="access">
              <LibrasIcon size={13} /> Libras
            </Chip>
          )}
          {vm.audio && (
            <Chip kind="access">
              <AudioIcon size={13} /> Audiodescrição
            </Chip>
          )}
          {vm.hasWheel && (
            <Chip kind="access">
              <WheelchairIcon size={13} /> Cadeirante
            </Chip>
          )}
        </div>
        {vm.experimental && (
          <span style={{ alignSelf: "flex-start" }}>
            <Chip kind="exp">Fonte em validação</Chip>
          </span>
        )}
      </div>
    </Link>
  );
}
