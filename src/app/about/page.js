import Link from "next/link";
import PageShapes from "@/components/PageShapes";
import styles from "./about.module.css";

export const metadata = {
  title: "About Sprinting Ink",
  description: "Learn about Sprinting Ink, a 3-minute creative writing game that trains your creativity, not your productivity.",
};

export default function AboutPage() {
  return (
    <div className={styles.aboutPage}>
      <PageShapes page="about" />
      
      <div className={`container ${styles.aboutContainer}`}>
        <div className={styles.header}>
          <h1 className={styles.title}>About Sprinting Ink</h1>
          <p className={styles.subtitle}>
            Three-minute creative sprints built to train your imagination instead of your typing speed.
          </p>
        </div>

        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>What is this?</h2>
          <div className={styles.textBlock}>
            <p>
              Sprinting Ink is a creative writing game. You get a random starter sentence. 
              You have exactly 3 minutes to keep the story going. Stop typing for 5 seconds, 
              and your words start to burn away.
            </p>
            <p>
              Once the clock hits zero, your draft hits the public feed for people to read, 
              vote on, and even continue.
            </p>
          </div>
        </div>

        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Why build it?</h2>
          <div className={styles.textBlock}>
            <p>
              Creativity is a muscle that needs resistance. Normal writing apps care about 
              word counts and deadlines. We care about the raw act of thinking under pressure. 
              No overthinking. No editing. No looking back.
            </p>
            <p>
              The vanish mechanic is not a punishment. It is liberation. Knowing your words 
              might disappear forces you to stop trying to be perfect. You just write something real.
            </p>
          </div>
        </div>

        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>How it helps</h2>
          <div className={styles.grid}>
            <div className={styles.featureCard}>
              <div className={styles.iconWrapper}>🧠</div>
              <h4 className={styles.featureTitle}>Forced Action</h4>
              <p className={styles.featureText}>
                Random prompts paired with a ticking clock means zero time for hesitation. Your instinct takes over.
              </p>
            </div>
            
            <div className={styles.featureCard}>
              <div className={styles.iconWrapper}>📖</div>
              <h4 className={styles.featureTitle}>Fresh Ideas</h4>
              <p className={styles.featureText}>
                Reading rapid-fire stories from strangers sparks concepts you would never brainstorm alone.
              </p>
            </div>
            
            <div className={styles.featureCard}>
              <div className={styles.iconWrapper}>✨</div>
              <h4 className={styles.featureTitle}>Vibe Check</h4>
              <p className={styles.featureText}>
                Getting upvotes tells you your style is working. No harsh critiques or long comments, just positive signals.
              </p>
            </div>
            
            <div className={styles.featureCard}>
              <div className={styles.iconWrapper}>🔗</div>
              <h4 className={styles.featureTitle}>Story Chains</h4>
              <p className={styles.featureText}>
                Picking up where someone else left off turns solo writing into a massive collaborative experiment.
              </p>
            </div>
          </div>
        </div>

        <div className={styles.ctaSection}>
          <h2 className={styles.ctaTitle}>Ready to write?</h2>
          <p className={styles.ctaText}>
            Your first sprint is totally free. No credit card required.
          </p>
          <Link href="/register" className={styles.ctaButton}>
            Start Writing
          </Link>
        </div>
      </div>
    </div>
  );
}
