// Types mirroring the backend `CulturalEvent` model (src/culturasp/models/event.py).
// Hand-written to match the API exactly; can later be generated from /openapi.json.

export type SchemaType =
  | "MusicEvent"
  | "ExhibitionEvent"
  | "TheaterEvent"
  | "ChildrensEvent"
  | "Event";
export type OCRStatus = "not_attempted" | "success" | "failed";

export interface ProgramItem {
  composer: string | null;
  work: string | null;
}

export interface AccessibilityInfo {
  sign_language: boolean;
  audio_description: boolean;
  wheelchair_seats: number | null;
  obese_seats: number | null;
  notes: string | null;
}

export interface TicketPolicy {
  free_of_charge: boolean;
  distribution_window: string | null;
  cancellation_window: string | null;
  external_url: string | null;
}

export interface CulturalEvent {
  id: string;
  source: string;
  source_url: string;
  title: string;
  start: string | null; // ISO datetime
  end: string | null;
  duration_minutes: number | null;
  schema_type: SchemaType;
  venue: string;
  min_age: number | null;
  max_age: number | null;
  audience: string | null;
  category: string | null;
  program: ProgramItem[];
  conductor: string | null;
  performers: string[];
  accessibility: AccessibilityInfo;
  ticket: TicketPolicy;
  seat_map_url: string | null;
  seat_map_text: string | null;
  ocr_status: OCRStatus;
  scraped_at: string;
}

export interface SourceStatus {
  source: string;
  layout_signature: string | null;
}

export interface Metrics {
  events_total: number;
  sources: string[];
}

export interface EventQuery {
  source?: string;
  date_from?: string;
  date_to?: string;
  accessible?: boolean;
  audience?: string;
  age?: number;
  limit?: number;
  offset?: number;
}

export type AccessibilityFeature = "libras" | "audio_description" | "wheelchair";
