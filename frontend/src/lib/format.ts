// PT-BR date/time formatting — ported from the design prototype's Component logic.

const MESF = [
  "janeiro", "fevereiro", "março", "abril", "maio", "junho",
  "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
];
const MESA = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"];
const DIAF = [
  "domingo", "segunda-feira", "terça-feira", "quarta-feira",
  "quinta-feira", "sexta-feira", "sábado",
];
const DIAA = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];

export const pad = (n: number): string => String(n).padStart(2, "0");

const cap = (s: string): string => s.replace(/^./, (c) => c.toUpperCase());

/** "10h50" or "20h" */
export function timeLabel(d: Date): string {
  const h = d.getHours();
  const m = d.getMinutes();
  return `${h}h${m ? pad(m) : ""}`;
}

/** "sáb · 10h50" */
export function whenLabel(d: Date): string {
  return `${DIAA[d.getDay()]} · ${timeLabel(d)}`;
}

/** "Sábado, 8 de agosto de 2026" */
export function dateFull(d: Date): string {
  return `${cap(DIAF[d.getDay()])}, ${d.getDate()} de ${MESF[d.getMonth()]} de ${d.getFullYear()}`;
}

/** "10 de maio – 20 de agosto de 2026" */
export function rangeFull(start: Date, end: Date): string {
  return `${start.getDate()} de ${MESF[start.getMonth()]} – ${end.getDate()} de ${MESF[end.getMonth()]} de ${end.getFullYear()}`;
}

/** "Até 20 ago" — cover text for an exhibition card */
export function coverRange(end: Date): string {
  return `Até ${end.getDate()} ${MESA[end.getMonth()].toLowerCase()}`;
}

export const coverDay = (d: Date): string => pad(d.getDate());
export const coverMonth = (d: Date): string => MESA[d.getMonth()];

export const isWeekend = (d: Date): boolean => d.getDay() === 0 || d.getDay() === 6;

/** "26 de junho de 2026" — used by the procedência banner */
export function dateLong(d: Date): string {
  return `${d.getDate()} de ${MESF[d.getMonth()]} de ${d.getFullYear()}`;
}

/** Parse an ISO string safely; returns null on missing/invalid. */
export function parseDate(iso: string | null): Date | null {
  if (!iso) return null;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? null : d;
}
