import Link from "next/link";
import styles from "./about.module.css";

export const metadata = {
  title: "About | Sprinting Ink",
  description: "Why we built a creative writing game that destroys your words.",
};

export default function AboutPage() {
  return (
    <div className={styles.aboutPage}>

      {/* ── ZONE 1: The Problem ─────────────────────────────────────── */}
      <section className={styles.problemSection}>
        <div className={styles.problemInner}>
          <div className={styles.problemLabel}>
            <span className={styles.eyebrow}>The Problem</span>
            <hr className={styles.problemLabelLine} />
          </div>
          <div className={styles.problemContent}>
            <h1 className={styles.headline}>
              Most writing apps are built for output. They want you to be a machine.
            </h1>
            <p className={styles.lead}>
              They track word counts. They hand you formatting toolbars. They let you rewrite your first sentence six times before you have written anything at all. That does not make you a better writer. It makes you a slower one.
            </p>
          </div>
        </div>
      </section>

      {/* ── Bridge label ────────────────────────────────────────────── */}
      <div className={styles.answerLabel}>
        <span className={styles.answerLabelText}>Our Answer</span>
        <hr className={styles.answerLabelLine} />
      </div>

      {/* ── ZONE 2: The Solutions ───────────────────────────────────── */}
      <section className={styles.solutionsSection}>
        <div className={styles.solutionsInner}>

          <div className={`${styles.point} ${styles.pointHero}`}>
            <div className={styles.pointMeta}>
              <span className={styles.pointNumber}>01</span>
            </div>
            <div>
              <h2 className={styles.pointTitle}>The Blank Page is a Trap</h2>
              <p className={styles.pointText}>
                Staring and waiting for inspiration is a waste of time. Sprinting Ink forces you to start. You get a bizarre sentence, you have three minutes, and you have no choice but to write.
              </p>
            </div>
          </div>

          <div className={styles.point}>
            <div className={styles.pointMeta}>
              <span className={styles.pointNumber}>02</span>
            </div>
            <div>
              <h2 className={styles.pointTitle}>Hesitation is Death</h2>
              <p className={styles.pointText}>
                Stop typing for five seconds and your words burn. Literally. It is not a gimmick. It is a trick to shut your inner critic up so your instincts can work.
              </p>
            </div>
          </div>

          <div className={styles.point}>
            <div className={styles.pointMeta}>
              <span className={styles.pointNumber}>03</span>
            </div>
            <div>
              <h2 className={styles.pointTitle}>Perfection is Fake</h2>
              <p className={styles.pointText}>
                Past sentences blur as you type. You cannot edit them. You cannot look back. The only direction is forward.
              </p>
            </div>
          </div>

          <div className={styles.point}>
            <div className={styles.pointMeta}>
              <span className={styles.pointNumber}>04</span>
            </div>
            <div>
              <h2 className={styles.pointTitle}>Writing is Multiplayer</h2>
              <p className={styles.pointText}>
                When the timer hits zero, your draft goes public. Strangers read it, vote on it, and can chain their own three minutes onto the end of yours.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* ── OUTRO ───────────────────────────────────────────────────── */}
      <div className={styles.outroSection}>
        <div className={styles.outroInner}>
          <h2 className={styles.outroTitle}>Stop thinking. Start sprinting.</h2>
          <Link href="/register" className={styles.ctaButton}>
            Play Now
          </Link>
        </div>
      </div>

    </div>
  );
}
