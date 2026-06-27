import { Link } from "react-router-dom";

function Stub({ title, note }: { title: string; note: string }) {
  return (
    <div className="container" style={{ paddingTop: 60, paddingBottom: 60, maxWidth: 720 }}>
      <h1 style={{ fontSize: 40, margin: "0 0 12px" }}>{title}</h1>
      <p style={{ fontSize: 18, color: "var(--cm)", lineHeight: 1.5 }}>{note}</p>
      <p style={{ marginTop: 20 }}>
        <Link to="/programacao" className="btn btn--primary">
          Ver a programação
        </Link>
      </p>
    </div>
  );
}

export const Accessibility = () => (
  <Stub
    title="Acessibilidade"
    note="Encontre eventos por recurso (Libras, audiodescrição, assentos para cadeirantes). Em construção — chega na próxima fase."
  />
);

export const Subscribe = () => (
  <Stub
    title="Assinar a agenda"
    note="Assine o feed iCal/RSS ou adicione ao seu calendário. Em construção — chega na próxima fase."
  />
);

export const DevPortal = () => (
  <Stub
    title="API & Dados Abertos"
    note="Documentação da API, fontes e status do serviço. Em construção — chega na próxima fase."
  />
);
