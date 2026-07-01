// Adapter: map the backend `CulturalEvent` into the view-model the UI components
// consume. ALL handoff↔API divergences are resolved here, in one place.
//
// Key decisions (honoring the non-negotiable "never invent data"):
//  - schema_type → PT-BR label + cover color.
//  - `venue` is just a name in the API (no address) → we show the name only.
//  - accessibility ausência → "Não informado" (never "não tem").
//  - single vs range derived from start/end spanning different days.

import {
  coverDay,
  coverMonth,
  coverRange,
  dateFull,
  dateLong,
  isWeekend,
  parseDate,
  rangeFull,
  timeLabel,
  whenLabel,
} from "./format";
import type { CulturalEvent, ProgramItem, SchemaType } from "./types";

export interface EventVM {
  id: string;
  source: string;
  sourceUrl: string;
  title: string;
  typeLabel: string;
  typeColor: string;
  // date/cover
  isRange: boolean;
  isSingle: boolean;
  isUndated: boolean;
  coverDay: string;
  coverMonth: string;
  coverRange: string;
  whenLabel: string;
  dateFull: string;
  timeLine: string;
  weekend: boolean;
  // venue (name only — API has no address)
  venueName: string;
  // programme
  program: ProgramItem[];
  hasProgram: boolean;
  conductor: string | null;
  performersLine: string;
  // accessibility
  free: boolean;
  libras: boolean;
  audio: boolean;
  wheelSeats: number | null;
  obeseSeats: number | null;
  hasWheel: boolean;
  hasAnyAccess: boolean;
  librasStatus: string;
  librasText: string;
  audioStatus: string;
  audioText: string;
  wheelStatus: string;
  wheelText: string;
  accNotes: string;
  ariaLabel: string;
  // ticket
  ticketDist: string;
  ticketCancel: string;
  externalUrl: string | null;
  // seat map (optional)
  seatMapUrl: string | null;
  // audience / age (children & family programming)
  audienceLabel: string;
  ageLabel: string;
  kidsLabel: string;
  isChildrens: boolean;
  category: string | null;
  // provenance
  scrapedAtLabel: string;
  experimental: boolean;
}

const TYPE_LABEL: Record<SchemaType, string> = {
  MusicEvent: "Concerto",
  ExhibitionEvent: "Exposição",
  TheaterEvent: "Teatro",
  ChildrensEvent: "Infantil",
  Event: "Evento",
};
const TYPE_COLOR: Record<SchemaType, string> = {
  MusicEvent: "#2E3A87", // indigo
  ExhibitionEvent: "#B92C77", // magenta
  TheaterEvent: "#0E7C5A", // green
  ChildrensEvent: "#C2410C", // orange
  Event: "#3A4A6B", // slate (generic)
};

// Audience label (PT-BR). Falls back to a capitalised form of the raw tag.
const AUDIENCE_LABEL: Record<string, string> = {
  infantil: "Infantil",
  livre: "Livre",
  familia: "Família",
  jovens: "Jovens",
};

function audienceLabel(a: string | null): string {
  if (!a) return "";
  return AUDIENCE_LABEL[a] ?? a.charAt(0).toUpperCase() + a.slice(1);
}

// Recommended age band → PT-BR label. Mirrors CulturalEvent.age_range_text.
function ageLabel(min: number | null, max: number | null): string {
  if (min == null && max == null) return "";
  if (max != null) return `${min ?? 0}–${max} anos`;
  if (!min) return "Livre"; // min 0/undefined, no upper bound
  return `A partir de ${min} anos`;
}

const NOT_INFORMED = "Não informado";
const NOT_INFORMED_SESSION = "Não informado pela fonte para esta sessão.";

export function toEventVM(e: CulturalEvent): EventVM {
  const s = parseDate(e.start);
  const end = parseDate(e.end);
  const isRange = !!(s && end && end.toDateString() !== s.toDateString());
  const isSingle = !!s && !isRange;
  const isUndated = !s;

  const acc = e.accessibility;
  const libras = acc.sign_language;
  const audio = acc.audio_description;
  const wheelSeats = acc.wheelchair_seats;
  const hasWheel = (wheelSeats ?? 0) > 0;

  const program = e.program.filter((p) => p.work || p.composer);

  let coverDayV = "—";
  let coverMonthV = "";
  let coverRangeV = "";
  let when = "Data a confirmar";
  let dateFullV = "Data a confirmar";
  let timeLine = "";
  let weekend = false;

  if (isRange && s && end) {
    coverRangeV = coverRange(end);
    when = `Em cartaz · até ${end.getDate()} ${coverMonth(end).toLowerCase()}`;
    dateFullV = rangeFull(s, end);
    timeLine = "Exposição";
    weekend = true; // exhibitions always pass the weekend filter (long-running)
  } else if (isSingle && s) {
    coverDayV = coverDay(s);
    coverMonthV = coverMonth(s);
    when = whenLabel(s);
    dateFullV = dateFull(s);
    timeLine = e.duration_minutes
      ? `Início às ${timeLabel(s)} · duração aprox. ${e.duration_minutes} min`
      : `Início às ${timeLabel(s)}`;
    weekend = isWeekend(s);
  }

  const typeLabel = TYPE_LABEL[e.schema_type] ?? "Evento";

  const audLabel = audienceLabel(e.audience);
  const ageLbl = ageLabel(e.min_age, e.max_age);
  // Combine into one chip label, avoiding a redundant "Livre · Livre".
  const kidsLabel =
    audLabel && ageLbl && audLabel !== ageLbl
      ? `${audLabel} · ${ageLbl}`
      : audLabel || ageLbl;
  const isChildrens = e.schema_type === "ChildrensEvent" || e.audience === "infantil";

  const ariaLabel =
    `${typeLabel}: ${e.title}. ${when}, ${e.source}.` +
    (e.ticket.free_of_charge ? " Gratuito." : "") +
    (libras ? " Libras disponível." : "") +
    (audio ? " Audiodescrição disponível." : "") +
    (audLabel ? ` Público: ${audLabel}.` : "");

  return {
    id: e.id,
    source: e.source,
    sourceUrl: e.source_url,
    title: e.title,
    typeLabel,
    typeColor: TYPE_COLOR[e.schema_type] ?? TYPE_COLOR.Event,
    isRange,
    isSingle,
    isUndated,
    coverDay: coverDayV,
    coverMonth: coverMonthV,
    coverRange: coverRangeV,
    whenLabel: when,
    dateFull: dateFullV,
    timeLine,
    weekend,
    venueName: e.venue,
    program,
    hasProgram: program.length > 0,
    conductor: e.conductor,
    performersLine: e.performers.join(" · "),
    free: e.ticket.free_of_charge,
    libras,
    audio,
    wheelSeats,
    obeseSeats: acc.obese_seats,
    hasWheel,
    hasAnyAccess: libras || audio || hasWheel,
    librasStatus: libras ? "Disponível" : NOT_INFORMED,
    librasText: libras ? "Intérprete de Libras durante o evento." : NOT_INFORMED_SESSION,
    audioStatus: audio ? "Disponível" : NOT_INFORMED,
    audioText: audio ? "Audiodescrição disponível na sessão." : NOT_INFORMED_SESSION,
    wheelStatus: hasWheel ? (wheelSeats != null ? `${wheelSeats} lugares` : "Disponível") : NOT_INFORMED,
    wheelText: hasWheel
      ? wheelSeats != null
        ? `${wheelSeats} assentos reservados para cadeirantes` +
          (acc.obese_seats ? ` · ${acc.obese_seats} assentos amplos` : "")
        : "Acesso para cadeirantes."
      : "Não informado pela fonte.",
    accNotes: acc.notes ?? "",
    ariaLabel,
    ticketDist: e.ticket.distribution_window ?? "",
    ticketCancel: e.ticket.cancellation_window ?? "",
    externalUrl: e.ticket.external_url,
    seatMapUrl: e.seat_map_url,
    audienceLabel: audLabel,
    ageLabel: ageLbl,
    kidsLabel,
    isChildrens,
    category: e.category,
    scrapedAtLabel: parseDate(e.scraped_at) ? dateLong(parseDate(e.scraped_at)!) : "",
    experimental: false, // API only serves live sources; experimental ones aren't returned
  };
}

/** Build the iCalendar (.ics) text for a single event, client-side. */
export function makeICS(e: CulturalEvent, vm: EventVM): string {
  const s = parseDate(e.start);
  const fmt = (d: Date) =>
    `${d.getFullYear()}${pad2(d.getMonth() + 1)}${pad2(d.getDate())}T${pad2(d.getHours())}${pad2(d.getMinutes())}00`;
  const lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CulturaSP//PT-BR//", "BEGIN:VEVENT"];
  lines.push(`UID:${e.id}@culturasp`);
  lines.push(`SUMMARY:${escapeICS(e.title)}`);
  if (s) {
    lines.push(`DTSTART:${fmt(s)}`);
    const end = parseDate(e.end) ?? new Date(s.getTime() + (e.duration_minutes ?? 60) * 60000);
    lines.push(`DTEND:${fmt(end)}`);
  }
  lines.push(`LOCATION:${escapeICS(vm.venueName)}`);
  lines.push(`DESCRIPTION:${escapeICS(`Fonte: ${e.source}. Confirme no site oficial: ${e.source_url}`)}`);
  lines.push("END:VEVENT", "END:VCALENDAR");
  return lines.join("\r\n");
}

const pad2 = (n: number) => String(n).padStart(2, "0");
const escapeICS = (s: string) => s.replace(/([,;\\])/g, "\\$1").replace(/\n/g, "\\n");
