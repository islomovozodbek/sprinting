"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import styles from "./page.module.css";
import MiniSprintDemo from "@/components/MiniSprintDemo";
import FogOfWarDemo from "@/components/FogOfWarDemo";
import BurnDemo from "@/components/BurnDemo";
import ScrollReveal from "@/components/ScrollReveal";
import PageShapes from "@/components/PageShapes";

function ScribbleLine() {
  return (
    <svg className={`${styles.floatingSvg} ${styles.heroSvgLeft}`} viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <path className={styles.svgStroke} d="M10 90 Q 50 10, 90 90 T 170 90" fill="transparent" stroke="var(--accent)" strokeWidth="3" strokeLinecap="round" />
      <path className={styles.svgStroke} d="M30 110 Q 70 150, 110 110 T 190 110" fill="transparent" stroke="var(--text-muted)" strokeWidth="3" strokeLinecap="round" strokeDasharray="5,5" />
    </svg>
  );
}

function ScribbleCircle() {
  return (
    <svg className={`${styles.floatingSvg} ${styles.heroSvgRight}`} viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <path className={styles.svgStroke} d="M100 20 C 150 20, 180 50, 180 100 C 180 150, 150 180, 100 180 C 50 180, 20 150, 20 100 C 20 60, 40 30, 80 25" fill="transparent" stroke="var(--accent)" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export default function Home() {
  const { user } = useAuth();
  const [authError, setAuthError] = useState("");



  useEffect(() => {
    if (typeof window !== "undefined" && window.location.hash) {
      const hashParams = new URLSearchParams(window.location.hash.substring(1));
      const hashErr = hashParams.get("error_description") || hashParams.get("error");
      if (hashErr) setAuthError(decodeURIComponent(hashErr));
    }
  }, []);

  return (
    <div className={styles.pageWrapper}>
      <PageShapes page="home" />
      {authError && (
        <div style={{ background: "red", color: "white", padding: 16, textAlign: "center", position: "relative", zIndex: 9999 }}>
          Login Error: {authError}
        </div>
      )}
      
      {/* ── Hero Section ── */}
      <section className={`${styles.hero} container`}>
        <ScribbleLine />
        <ScribbleCircle />
        
        <ScribbleLine />
        <ScribbleCircle />
        





        <div className={styles.heroInner}>

          <ScrollReveal animation="fadeUp" delay={100}>
            <h1 className={styles.heroTitle}>
              <span className={styles.heroLine}>The less you fear</span>
              <span className={styles.heroLine}>the better you write</span>
            </h1>
          </ScrollReveal>

          <ScrollReveal animation="fadeUp" delay={200}>
            <p className={styles.heroSubtitle}>
              Your words disappear if you stop. So don&apos;t stop.
              Get a prompt, write for 3 minutes, and never look back.
            </p>
          </ScrollReveal>

          <ScrollReveal animation="fadeUp" delay={300}>
            <div className={styles.heroCTA}>
              <Link href={user ? "/sprint" : "/register"} className="btn btn-primary btn-lg">
                Start Writing — It&apos;s Free
              </Link>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Split Sections (How it works) ── */}
      <section className={styles.splitSection}>
        <div className={`container ${styles.splitGrid}`}>
          <div className={styles.splitContent}>
            <ScrollReveal animation="slideLeft" delay={100}>
              <h2>The perfect blank page.</h2>
              <p>
                We’ve stripped away every distraction. No formatting tools, no spellcheck, no word counts to obsess over. Just you, stark typography, and a blank canvas inspired by the cleanest editors in the world.
              </p>
              <ul className="text-secondary" style={{ listStyle: "none", display: "grid", gap: "12px", paddingLeft: 0 }}>
                <li>✓ Ultra-minimal Zenpen-style interface</li>
                <li>✓ Beautiful typography that makes words shine</li>
                <li>✓ Full-screen focus mode</li>
              </ul>
            </ScrollReveal>
          </div>
          <div className={styles.splitVisual}>
            <ScrollReveal animation="scaleUp" delay={200}>
              <MiniSprintDemo />
            </ScrollReveal>
          </div>
        </div>
      </section>

      <section className={`${styles.splitSection} ${styles.splitReverse}`}>
        <div className={`container ${styles.splitGrid}`}>
          <div className={styles.splitContent}>
            <ScrollReveal animation="slideRight" delay={100}>
              <h2>The Fog of War.</h2>
              <p>
                Perfectionism is the enemy of the first draft. In Sprinting Ink, as you type, your older sentences blur out like drying ink. You can&apos;t go back to edit them. You can only move forward.
              </p>
{/* <Link href="/feed" className="btn btn-secondary mt-4">
                Read the survivors
              </Link> */}
            </ScrollReveal>
          </div>
          <div className={styles.splitVisual} style={{ position: "relative" }}>
            <ScrollReveal animation="scaleUp" delay={200}>
              <svg style={{ position: "absolute", top: -40, left: -40, width: 100, zIndex: 0, opacity: 0.5 }} viewBox="0 0 100 100">
                <path d="M50 0 L100 50 L50 100 L0 50 Z" fill="var(--bg-secondary)" />
              </svg>
              <FogOfWarDemo />
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* ── Feature 3: Pause and Burn ── */}
      <section className={styles.splitSection}>
        <div className={`container ${styles.splitGrid}`}>
          <div className={styles.splitContent}>
            <ScrollReveal animation="slideLeft" delay={100}>
              <h2>Keep moving or burn.</h2>
              <p>
                Hesitation is death. If you stop typing for 5 seconds, the screen bleeds red, and your current thought burns away forever. Sprinting Ink forces you to bypass your inner critic by making speed your only option.
              </p>
            </ScrollReveal>
          </div>
          <div className={styles.splitVisual} style={{ position: "relative" }}>
            <ScrollReveal animation="scaleUp" delay={200}>
              <BurnDemo />
            </ScrollReveal>
          </div>
        </div>
      </section>

      <section className={styles.freeSection}>
        <ScrollReveal animation="fadeUp">
          <div className="container">
            <h2>Free to write. Free to explore.</h2>
            <p>Unlimited sprints, custom prompts, and your own writing pace. Every feature is free for everyone.</p>
            <Link href={user ? "/sprint" : "/register"} className="btn btn-primary btn-lg">
              Start Writing
            </Link>
          </div>
        </ScrollReveal>
      </section>

      {/* ── Footer ── */}
      <footer className={styles.footer}>
        <div className="container">
          <div className={styles.footerInner}>
            <div className={styles.footerBrand}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "1.5rem" }}>⌨️</span>
                <span style={{ fontFamily: "var(--font-heading)", fontSize: "1.2rem", fontWeight: 700 }}>
                  sprinting<span style={{ color: "var(--accent)" }}> ink</span>
                </span>
              </div>
              <p>3-minute creative sprints to train your brain. Forget productivity, embrace creativity.</p>
            </div>

            <div className={styles.footerCol}>
              <h4>Explore</h4>
              <Link href="/feed">Story Feed</Link>
              <Link href="/leaderboard">Leaderboards</Link>
              <Link href={user ? "/sprint" : "/register"}>Start Writing</Link>
            </div>

            <div className={styles.footerCol}>
              <h4>Connect</h4>
              <Link href="/about">About Us</Link>
              <Link href="/search">Find Writers</Link>
              <Link href="/contact">Contact</Link>
            </div>
          </div>

          <div className={styles.footerBottom}>
            <span>© 2026 Sprinting Ink. All rights reserved.</span>
            <span>Minimalist design inspired by focus.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
