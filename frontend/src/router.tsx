import { createBrowserRouter } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Accessibility } from "./routes/Accessibility";
import { Detail, NotFound } from "./routes/Detail";
import { DevPortal } from "./routes/Dev";
import { Home } from "./routes/Home";
import { Kit } from "./routes/Kit";
import { List } from "./routes/List";
import { Subscribe } from "./routes/Subscribe";

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
      { path: "/kit", element: <Kit /> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);
