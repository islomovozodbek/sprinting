import PageShapes from "@/components/PageShapes";

export const metadata = {
  title: "Contact — Sprinting Ink",
  description: "Get in touch with the creator of Sprinting Ink.",
};

export default function ContactPage() {
  return (
    <div style={{ padding: "var(--space-3xl) 0", minHeight: "calc(100vh - var(--nav-height))", position: "relative", overflow: "hidden" }}>
      <PageShapes page="about" />
      
      <div className="container" style={{ maxWidth: "700px" }}>
        <div className="text-center" style={{ marginBottom: "var(--space-3xl)" }}>
          <h1 style={{ marginBottom: "var(--space-md)" }}>Contact</h1>
          <p className="text-lg">
            Have questions, feedback, or just want to say hi? Get in touch!
          </p>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2xl)" }}>
          <section className="card" style={{ padding: "var(--space-xl)", textAlign: "center" }}>
            <h2 style={{ marginBottom: "var(--space-md)" }}>Email</h2>
            <p>
              <a href="mailto:islomovozodbek77@gmail.com" style={{ color: "var(--accent)", fontSize: "1.2rem", fontWeight: "bold", textDecoration: "none" }}>
                islomovozodbek77@gmail.com
              </a>
            </p>
          </section>

          <section className="card" style={{ padding: "var(--space-xl)", textAlign: "center" }}>
            <h2 style={{ marginBottom: "var(--space-md)" }}>Telegram</h2>
            <p>
              <a href="https://t.me/shkrlvc" target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)", fontSize: "1.2rem", fontWeight: "bold", textDecoration: "none" }}>
                @shkrlvc
              </a>
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
