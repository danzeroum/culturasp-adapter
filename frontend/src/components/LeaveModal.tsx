import { useEffect, useRef } from "react";
import { ExternalIcon } from "../lib/icons";

export function LeaveModal({
  name,
  url,
  onCancel,
}: {
  name: string;
  url: string;
  onCancel: () => void;
}) {
  const confirmRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    confirmRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    // Backdrop. Keyboard users dismiss via Escape (handled above) or the Cancel
    // button; the click-to-dismiss here is a supplementary mouse affordance.
    // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions
    <div
      onClick={(e) => {
        if (e.target === e.currentTarget) onCancel();
      }}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,16,12,.5)",
        display: "grid",
        placeItems: "center",
        zIndex: 150,
        padding: 18,
        animation: "csp-fade .2s ease",
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="leave-title"
        style={{
          background: "var(--cb)",
          borderRadius: 16,
          maxWidth: 420,
          width: "100%",
          padding: 26,
          textAlign: "center",
          animation: "csp-pop .22s ease",
          border: "1px solid var(--cl)",
        }}
      >
        <span style={{ width: 46, height: 46, borderRadius: 12, background: "var(--weekend-bg)", color: "var(--brand)", display: "inline-grid", placeItems: "center", marginBottom: 12 }}>
          <ExternalIcon size={22} />
        </span>
        <h2 id="leave-title" style={{ fontSize: 22, margin: "0 0 8px" }}>
          Você está saindo do CulturaSP
        </h2>
        <p style={{ fontSize: 15, color: "var(--cm)", lineHeight: 1.5, margin: "0 0 20px" }}>
          A retirada de ingressos é feita no site oficial de <strong>{name}</strong>. O CulturaSP não
          vende ingressos.
        </p>
        <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
          <button type="button" onClick={onCancel} className="btn btn--secondary">
            Cancelar
          </button>
          <a
            ref={confirmRef}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={onCancel}
            className="btn btn--primary"
          >
            Continuar
            <ExternalIcon size={17} />
          </a>
        </div>
      </div>
    </div>
  );
}
