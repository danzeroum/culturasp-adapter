import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from "react";
import { CheckIcon } from "../lib/icons";

const Ctx = createContext<((msg: string) => void) | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [msg, setMsg] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const show = useCallback((m: string) => {
    if (timer.current) clearTimeout(timer.current);
    setMsg(m);
    timer.current = setTimeout(() => setMsg(null), 3600);
  }, []);

  return (
    <Ctx.Provider value={show}>
      {children}
      {/* polite live region so screen readers announce the toast */}
      <div aria-live="polite" role="status">
        {msg ? (
          <div
            style={{
              position: "fixed",
              left: "50%",
              bottom: 28,
              transform: "translateX(-50%)",
              background: "var(--dark-band)",
              color: "var(--dark-band-tx)",
              padding: "12px 18px",
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              gap: 9,
              fontSize: 14.5,
              fontWeight: 600,
              boxShadow: "0 14px 30px -18px rgba(0,0,0,.6)",
              zIndex: 200,
              animation: "csp-pop .22s ease",
            }}
          >
            <span style={{ color: "var(--toast-check)", display: "inline-flex" }}>
              <CheckIcon size={16} />
            </span>
            {msg}
          </div>
        ) : null}
      </div>
    </Ctx.Provider>
  );
}

export function useToast(): (msg: string) => void {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
