import { createBrowserRouter } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Detail, NotFound } from "./routes/Detail";
import { Home } from "./routes/Home";
import { List } from "./routes/List";
import { Accessibility, DevPortal, Subscribe } from "./routes/Stubs";

export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/programacao", element: <List /> },
      { path: "/eventos/:id", element: <Detail /> },
      { path: "/acessibilidade", element: <Accessibility /> },
      { path: "/assinar", element: <Subscribe /> },
      { path: "/dev", element: <DevPortal /> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);
