// Central i18n catalog. pt-BR is the primary (and currently only) locale.
//
// Keeping every user-facing string here is the foundation for future locales
// and keeps the copy consistent and reviewable in one place. Components import
// `t` and read nested keys (e.g. `t.list.title`); strings with runtime values
// use the `fmt()` helper for `{placeholder}` interpolation.
//
// To add a locale later: duplicate this object, translate the leaves, and wire
// a locale selector that swaps which catalog `t` points to. The shape is frozen
// `as const` so missing/renamed keys surface as TypeScript errors.

export const locale = "pt-BR";

export const t = {
  app: {
    name: "CulturaSP",
    tagline: "portal de dados culturais abertos",
  },

  nav: {
    label: "Principal",
    programacao: "Programação",
    acessibilidade: "Acessibilidade",
    dadosAbertos: "Dados abertos",
    themeToLight: "Ativar tema claro",
    themeToDark: "Ativar tema escuro",
  },

  layout: {
    skipToContent: "Pular para o conteúdo",
  },

  footer: {
    label: "Rodapé",
    blurb: "CulturaSP · portal de dados culturais abertos. Não vende ingressos — sempre confirme na fonte oficial.",
    dadosAbertos: "Dados abertos",
    repo: "Repositório ↗",
    repoUrl: "https://github.com/danzeroum/culturasp-adapter",
  },

  home: {
    eyebrow: "Dados culturais abertos · São Paulo",
    heroTitle: "A programação cultural de SP, acessível a todos.",
    heroLede:
      "Descubra concertos e exposições, filtre por recursos de acessibilidade e seja levado ao canal oficial para retirar seu ingresso.",
    searchLabel: "Buscar eventos",
    searchPlaceholder: "Buscar por evento, artista ou local…",
    searchSubmit: "Explorar",
    chipAccessible: "Acessível",
    chipWeekend: "Este fim de semana",
    chipFree: "Gratuito",
    upcoming: "Próximos eventos",
    seeAll: "Ver toda a programação →",
    subscribeTitle: "Leve a agenda com você",
    subscribeLede: "Assine o feed iCal/RSS ou adicione ao seu calendário.",
    subscribeCta: "Assinar agenda",
  },

  list: {
    title: "Programação",
    // fmt(t.list.summaryCount, { count }) → "12 eventos"
    summaryCount: "{count} eventos",
    summarySource: "fonte oficial: Sala São Paulo",
    filters: "Filtros",
    filtersOpen: "Filtros",
    filtersClose: "Fechar filtros",
    clear: "Limpar",
    periodo: "Período",
    weekend: "Fim de semana",
    a11yGroup: "Acessibilidade",
    a11ySwitch: "Com recursos de acessibilidade",
    a11yHint: "Libras, audiodescrição ou assentos para cadeirantes.",
    tipo: "Tipo",
    tipoConcerto: "Concerto",
    tipoExposicao: "Exposição",
    onlyFree: "Somente gratuitos",
    bitAccessible: "acessível",
    bitWeekend: "fim de semana",
    bitFree: "gratuito",
  },

  states: {
    emptyTitle: "Nenhum evento com esses filtros",
    emptyLede: "Tente afrouxar a busca — incluir dias de semana, eventos pagos ou outras fontes.",
    emptyClear: "Limpar filtros",
    errorTitle: "Não foi possível carregar",
    errorLede: "Verifique sua conexão. Os dados podem estar desatualizados — confirme sempre na fonte oficial.",
    errorRetry: "Tentar de novo",
    loading: "Carregando…",
  },
} as const;

/** Interpolate `{placeholder}` tokens in a catalog string. */
export function fmt(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, key) => {
    const v = vars[key];
    return v === undefined ? `{${key}}` : String(v);
  });
}
