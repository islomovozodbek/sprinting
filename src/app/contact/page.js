import PageShapes from "@/components/PageShapes";
import styles from "./contact.module.css";

export const metadata = {
  title: "Contact — Sprinting Ink",
  description: "Get in touch with the creator of Sprinting Ink.",
};

export default function ContactPage() {
  return (
    <div className={styles.contactPage}>
      <PageShapes page="about" />
      
      <div className={`container ${styles.contactContainer}`}>
        <div className={styles.header}>
          <h1 className={styles.title}>Let's Connect</h1>
          <p className={styles.subtitle}>
            Have questions, feedback, or just want to say hi? I'd love to hear from you. Choose your preferred way to reach out below.
          </p>
        </div>

        <div className={styles.grid}>
          {/* Email Card */}
          <div className={styles.card}>
            <div className={styles.iconWrapper}>
              <svg className={styles.svgIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </svg>
            </div>
            <h2 className={styles.cardTitle}>Email</h2>
            <p className={styles.cardDescription}>
              For detailed inquiries, feedback, or support requests.
            </p>
            <a href="mailto:islomovozodbek77@gmail.com" className={styles.link}>
              islomovozodbek77@gmail.com
            </a>
          </div>

          {/* Telegram Card */}
          <div className={styles.card}>
            <div className={styles.iconWrapper}>
              <svg className={styles.svgIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </div>
            <h2 className={styles.cardTitle}>Telegram</h2>
            <p className={styles.cardDescription}>
              For quick questions, casual chats, or fast responses.
            </p>
            <a href="https://t.me/shkrlvc" target="_blank" rel="noopener noreferrer" className={styles.link}>
              @shkrlvc
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
