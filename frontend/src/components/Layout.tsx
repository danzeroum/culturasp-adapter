import { Outlet } from "react-router-dom";
import { t } from "../lib/i18n";
import { Footer } from "./Footer";
import { Header } from "./Header";

export function Layout() {
  return (
    <>
      <a className="skip-link" href="#main">
        {t.layout.skipToContent}
      </a>
      <Header />
      <main id="main">
        <Outlet />
      </main>
      <Footer />
    </>
  );
}
