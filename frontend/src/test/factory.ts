import type { CulturalEvent } from "../lib/types";

/** Build a CulturalEvent for tests, matching the backend shape. */
export function makeEvent(overrides: Partial<CulturalEvent> = {}): CulturalEvent {
  return {
    id: "sala-sp:1727",
    source: "Sala São Paulo",
    source_url: "https://salasaopaulo.art.br/salasp/pt/concerto/1727",
    title: "Orquestra Antares — Matinais",
    start: "2026-08-08T10:50:00",
    end: "2026-08-08T11:50:00",
    duration_minutes: 60,
    schema_type: "MusicEvent",
    venue: "Sala São Paulo",
    program: [
      { composer: "Mozart", work: "Sinfonia nº 40" },
      { composer: "Händel", work: "Water Music" },
    ],
    conductor: "Fábio Prado",
    performers: ["Orquestra Antares"],
    accessibility: {
      sign_language: true,
      audio_description: true,
      wheelchair_seats: 15,
      obese_seats: 14,
      notes: "Audiodescrição mediante reserva.",
    },
    ticket: {
      free_of_charge: true,
      distribution_window: "a partir das 12h, 3 dias antes",
      cancellation_window: "até 48h antes",
      external_url: "https://ingressos.salasaopaulo.art.br/evento/1727",
    },
    seat_map_url: null,
    seat_map_text: null,
    ocr_status: "not_attempted",
    scraped_at: "2026-06-26T12:00:00",
    ...overrides,
  };
}
