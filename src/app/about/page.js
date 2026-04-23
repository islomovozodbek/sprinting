import Link from "next/link";
import PageShapes from "@/components/PageShapes";
import styles from "./about.module.css";

export const metadata = {
  title: "Manifesto | Sprinting Ink",
  description: "Read the Sprinting Ink manifesto. Why we built a game that destroys your writing.",
};

export default function AboutPage() {
  return (
    <div className={styles.manifestoPage}>
      <PageShapes page="about" />
      
      <div className={`container ${styles.manifestoContainer}`}>
        <div className={styles.introBlock}>
          <p className={styles.eyebrow}>The Problem</p>
          <h1 className={styles.headline}>
            Most writing apps are built for output. They want you to be a machine.
          </h1>
          <p className={styles.lead}>
            They track your word counts. They give you formatting tools. They let you endlessly revise your first sentence until you lose your mind. This does not make you a better writer. It makes you a slow one.
          </p>
        </div>

        <div className={styles.divider}></div>

        <div className={styles.manifestoContent}>
          <div className={styles.point}>
            <span className={styles.pointNumber}>01.</span>
            <div className={styles.pointTextContent}>
              <h2 className={styles.pointTitle}>The Blank Page is a Trap</h2>
              <p className={styles.pointText}>
                Staring at a blank document waiting for inspiration is a waste of time. Sprinting Ink forces you to start. You are given a bizarre sentence. You have exactly three minutes. You have no choice but to write.
              </p>
            </div>
          </div>

          <div className={styles.point}>
            <span className={styles.pointNumber}>02.</span>
            <div className={styles.pointTextContent}>
              <h2 className={styles.pointTitle}>Hesitation is Death</h2>
              <p className={styles.pointText}>
                If you stop typing for five seconds, your words burn. Literally. They vanish from the screen. This is not a gimmick. It is a psychological trick to bypass your inner critic. Your subconscious has to take the wheel.
              </p>
            </div>
          </div>

          <div className={styles.point}>
            <span className={styles.pointNumber}>03.</span>
            <div className={styles.pointTextContent}>
              <h2 className={styles.pointTitle}>Perfection is Fake</h2>
              <p className={styles.pointText}>
                The fog of war blurs your past sentences. You cannot edit. You cannot look back. You must move forward. By removing the ability to polish, we force you to focus entirely on the raw act of creating.
              </p>
            </div>
          </div>

          <div className={styles.point}>
            <span className={styles.pointNumber}>04.</span>
            <div className={styles.pointTextContent}>
              <h2 className={styles.pointTitle}>Writing is Multiplayer</h2>
              <p className={styles.pointText}>
                When the timer hits zero, your survival draft goes public. Strangers read it. They upvote it. They can even chain their own three-minute sprint onto the end of yours. Writing stops being lonely.
              </p>
            </div>
          </div>
        </div>

        <div className={styles.outroBlock}>
          <h2 className={styles.outroTitle}>Stop Thinking. Start Sprinting.</h2>
          <Link href="/register" className={styles.ctaButton}>
            Play Now
          </Link>
        </div>
      </div>
    </div>
  );
}
