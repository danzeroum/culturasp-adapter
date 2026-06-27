import { expect, test } from "@playwright/test";

// Smoke test: every primary link/button reaches its route/handler, and the
// backend calls behind each screen succeed. Driven against the seeded API
// (one event: sala-sp:1727). Ported from the manual validation click-through.

const EVID = "sala-sp:1727";

test.describe("navegação e links (desktop)", () => {
  test("Home carrega (hero)", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /acessível a todos/ })).toBeVisible();
  });

  test("Header navega para cada rota", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Programação", exact: true }).first().click();
    await expect(page).toHaveURL(/\/programacao$/);
    await page.goBack();
    await page.getByRole("link", { name: /Acessibilidade/ }).first().click();
    await expect(page).toHaveURL(/\/acessibilidade/);
    await page.goBack();
    await page.getByRole("link", { name: "Dados abertos", exact: true }).first().click();
    await expect(page).toHaveURL(/\/dev$/);
  });

  test("Toggle de tema alterna data-theme", async ({ page }) => {
    await page.goto("/");
    const before = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    await page.getByRole("button", { name: /tema/ }).click();
    const after = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    expect(after).not.toBe(before);
  });

  test("Chips do hero filtram a lista", async ({ page }) => {
    for (const [label, frag] of [
      ["Acessível", "accessible=true"],
      ["Este fim de semana", "weekend=true"],
      ["Gratuito", "free=true"],
    ] as const) {
      await page.goto("/");
      await page.getByRole("link", { name: label, exact: true }).click();
      await expect(page).toHaveURL(new RegExp(frag.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
    }
  });

  test("Busca, ver-tudo, assinar e card de evento", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("searchbox", { name: "Buscar eventos" }).fill("antares");
    await page.getByRole("button", { name: "Explorar" }).click();
    await expect(page).toHaveURL(/\/programacao/);

    await page.goto("/");
    await page.getByRole("link", { name: /Ver toda a programação/ }).click();
    await expect(page).toHaveURL(/\/programacao$/);

    await page.goto("/");
    await page.getByRole("link", { name: "Assinar agenda" }).click();
    await expect(page).toHaveURL(/\/assinar/);

    await page.goto("/");
    await page.getByRole("link", { name: /Orquestra Antares/ }).first().click();
    await expect(page).toHaveURL(/\/eventos\//);
  });

  test("Footer: link do repositório aponta ao GitHub", async ({ page }) => {
    await page.goto("/");
    const repo = page.getByRole("link", { name: /Repositório/ });
    expect(await repo.getAttribute("href")).toContain("github.com/danzeroum/culturasp-adapter");
  });
});

test.describe("Detalhe (GET /v1/events/{id})", () => {
  test("carrega e todos os botões/links funcionam", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.goto(`/eventos/${EVID}`);
    await expect(page.getByRole("heading", { name: /Orquestra Antares/ })).toBeVisible();

    // JSON-LD link target
    const jl = page.getByRole("link", { name: /Ver JSON-LD/ });
    const href = await jl.getAttribute("href");
    expect(href).toContain("/v1/events/");
    expect(href).toContain("jsonld");

    // Add to calendar → .ics download + toast
    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: "Adicionar ao calendário" }).click(),
    ]);
    expect(download.suggestedFilename()).toMatch(/\.ics$/);
    await expect(page.getByText(/adicionado ao calendário/)).toBeVisible();

    // Share → clipboard + toast
    await page.getByRole("button", { name: "Compartilhar" }).click();
    await expect(page.getByText(/Link do evento copiado/)).toBeVisible();

    // Ticket CTA → leave modal → external official link → cancel
    await page.getByRole("button", { name: /Retirar no site oficial/ }).click();
    const modal = page.getByRole("dialog");
    await expect(modal).toBeVisible();
    const cont = modal.getByRole("link", { name: /Continuar/ });
    expect(await cont.getAttribute("href")).toContain("ingressos.salasaopaulo.art.br");
    await modal.getByRole("button", { name: "Cancelar" }).click();
    await expect(page.getByRole("dialog")).toBeHidden();

    // Back link
    await page.getByRole("link", { name: /Voltar à programação/ }).click();
    await expect(page).toHaveURL(/\/programacao/);
  });
});

test.describe("Lista — filtros em bottom-sheet (mobile)", () => {
  test.use({ viewport: { width: 390, height: 820 } });

  test("sidebar colapsa, FAB abre o sheet, filtro reflete na URL", async ({ page }) => {
    await page.goto("/programacao");
    await expect(page.getByRole("complementary", { name: "Filtros" })).toBeHidden();
    const fab = page.getByRole("button", { name: "Filtros" });
    await expect(fab).toBeVisible();
    await fab.click();
    const sheet = page.getByRole("dialog", { name: "Filtros" });
    await expect(sheet).toBeVisible();
    await sheet.getByRole("switch", { name: "Com recursos de acessibilidade" }).click();
    await expect(page).toHaveURL(/accessible=true/);
    await sheet.getByRole("button", { name: "Fechar filtros" }).click();
    await expect(page.getByRole("dialog", { name: "Filtros" })).toBeHidden();
  });
});

test.describe("Lista — filtros em sidebar (desktop)", () => {
  test("sidebar visível, FAB oculto", async ({ page }) => {
    await page.goto("/programacao");
    await expect(page.getByRole("complementary", { name: "Filtros" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Filtros" })).toBeHidden();
  });
});

test.describe("Acessibilidade (GET /v1/accessibility)", () => {
  test("rádios trocam ?feature=", async ({ page }) => {
    await page.goto("/acessibilidade");
    await page.getByRole("radio", { name: /Audiodescrição/ }).click();
    await expect(page).toHaveURL(/feature=audio_description/);
    await page.getByRole("radio", { name: "Cadeirante" }).click();
    await expect(page).toHaveURL(/feature=wheelchair/);
  });
});

test.describe("Assinar (feeds)", () => {
  test("campos de feed e ações de calendário", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.goto("/assinar");
    const ics = page.getByRole("textbox", { name: /URL do feed iCal/ });
    expect(await ics.inputValue()).toContain("/v1/events.ics");
    await page.getByRole("button", { name: "Copiar" }).first().click();
    await expect(page.getByText("URL copiada")).toBeVisible();
    const gcal = page.getByRole("link", { name: /Google Calendar/ });
    expect(await gcal.getAttribute("href")).toContain("calendar.google.com");
  });
});

test.describe("Dev e 404", () => {
  test("Swagger, Kit e rota desconhecida", async ({ page }) => {
    await page.goto("/dev");
    const swagger = page.getByRole("link", { name: /Abrir Swagger/ });
    expect(await swagger.getAttribute("href")).toContain("/docs");
    await page.getByRole("link", { name: /Kit de componentes/ }).click();
    await expect(page).toHaveURL(/\/kit$/);

    await page.goto("/rota-inexistente");
    await expect(page.getByText("404")).toBeVisible();
    await page.getByRole("link", { name: /Voltar ao início/ }).click();
    await expect(page).toHaveURL(/\/$/);
  });
});
