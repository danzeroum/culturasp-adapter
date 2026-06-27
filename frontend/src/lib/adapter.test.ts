import { describe, expect, it } from "vitest";
import { makeEvent } from "../test/factory";
import { makeICS, toEventVM } from "./adapter";

describe("toEventVM", () => {
  it("maps a single concert with PT-BR formatting", () => {
    const vm = toEventVM(makeEvent());
    expect(vm.typeLabel).toBe("Concerto");
    expect(vm.typeColor).toBe("#2E3A87");
    expect(vm.isSingle).toBe(true);
    expect(vm.isRange).toBe(false);
    expect(vm.coverDay).toBe("08");
    expect(vm.coverMonth).toBe("AGO");
    expect(vm.dateFull).toBe("Sábado, 8 de agosto de 2026");
    expect(vm.timeLine).toBe("Início às 10h50 · duração aprox. 60 min");
    expect(vm.weekend).toBe(true); // 2026-08-08 is a Saturday
    expect(vm.venueName).toBe("Sala São Paulo");
  });

  it("derives accessibility status with seat counts", () => {
    const vm = toEventVM(makeEvent());
    expect(vm.libras).toBe(true);
    expect(vm.librasStatus).toBe("Disponível");
    expect(vm.hasWheel).toBe(true);
    expect(vm.wheelStatus).toBe("15 lugares");
    expect(vm.wheelText).toContain("15 assentos");
    expect(vm.wheelText).toContain("14 assentos amplos");
    expect(vm.ariaLabel).toContain("Libras disponível");
  });

  it("labels missing accessibility as 'Não informado' (never invents)", () => {
    const vm = toEventVM(
      makeEvent({
        accessibility: { sign_language: false, audio_description: false, wheelchair_seats: null, obese_seats: null, notes: null },
      }),
    );
    expect(vm.libras).toBe(false);
    expect(vm.librasStatus).toBe("Não informado");
    expect(vm.hasWheel).toBe(false);
    expect(vm.hasAnyAccess).toBe(false);
  });

  it("maps an exhibition date range", () => {
    const vm = toEventVM(
      makeEvent({
        schema_type: "ExhibitionEvent",
        start: "2026-05-10T00:00:00",
        end: "2026-08-20T00:00:00",
        duration_minutes: null,
        program: [],
      }),
    );
    expect(vm.typeLabel).toBe("Exposição");
    expect(vm.typeColor).toBe("#B92C77");
    expect(vm.isRange).toBe(true);
    expect(vm.coverRange).toBe("Até 20 ago");
    expect(vm.dateFull).toBe("10 de maio – 20 de agosto de 2026");
    expect(vm.hasProgram).toBe(false);
    expect(vm.weekend).toBe(true);
  });

  it("handles an undated event gracefully", () => {
    const vm = toEventVM(makeEvent({ start: null, end: null }));
    expect(vm.isUndated).toBe(true);
    expect(vm.whenLabel).toBe("Data a confirmar");
    expect(vm.dateFull).toBe("Data a confirmar");
  });
});

describe("makeICS", () => {
  it("produces a VCALENDAR with DTSTART/DTEND derived from start+duration", () => {
    const e = makeEvent();
    const ics = makeICS(e, toEventVM(e));
    expect(ics).toContain("BEGIN:VCALENDAR");
    expect(ics).toContain("SUMMARY:Orquestra Antares — Matinais");
    expect(ics).toContain("DTSTART:20260808T105000");
    expect(ics).toContain("DTEND:20260808T115000");
    expect(ics).toContain("END:VCALENDAR");
  });
});
