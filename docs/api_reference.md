# Referência da API (OpenAPI)

A especificação completa está em [`openapi.json`](openapi.json) e é renderizada abaixo
via Swagger UI. Em runtime, a API também serve `/docs` (Swagger) e `/openapi.json`.

<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
<script>
  window.addEventListener("load", function () {
    window.ui = SwaggerUIBundle({
      // openapi.json fica na raiz do site; esta página usa directory URLs (/api_reference/).
      url: "../openapi.json",
      dom_id: "#swagger-ui",
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis],
    });
  });
</script>
