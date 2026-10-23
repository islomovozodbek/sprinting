"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import styles from "./leaderboard.module.css";
import ScrollReveal from "@/components/ScrollReveal";
import PageShapes from "@/components/PageShapes";

const CATEGORIES = [
  { id: "quality", label: "Global Ranking (Upvotes)", sortKey: "total_upvotes_received", unit: "Upvotes" },
  { id: "dedication", label: "Most Sprints (Activity)", sortKey: "total_stories", unit: "Sprints" },
  { id: "consistency", label: "Longest Streaks (Consistency)", sortKey: "current_streak", unit: "Days" },
];

export default function LeaderboardPage() {
  const [activeCategory, setActiveCategory] = useState(CATEGORIES[0]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const fetchLeaderboard = async () => {
      setLoading(true);
      setError(null);
      try {
        // Each source's top 20 contains every candidate for the combined top 20.
        const collectionQuery = supabase
          .from("collection_rankings")
          .select("id,username,profile_color,total_stories,total_upvotes_received");
        if (activeCategory.id !== "consistency") {
          collectionQuery.order(activeCategory.sortKey, { ascending: false });
        }
        const [writers, collection] = await Promise.all([
          supabase.from("profiles")
            .select("id,username,profile_color,total_stories,total_upvotes_received,current_streak")
            .order(activeCategory.sortKey, { ascending: false, nullsFirst: false })
            .order("id", { ascending: true }).limit(20),
          collectionQuery.order("id", { ascending: true }).limit(20),
        ]);
        if (writers.error || collection.error) throw writers.error || collection.error;
        if (cancelled) return;
        const combined = [
          ...(writers.data || []),
          ...(collection.data || []).map(profile => ({ ...profile, current_streak: 0 })),
        ];
        combined.sort((a, b) =>
          (b[activeCategory.sortKey] || 0) - (a[activeCategory.sortKey] || 0)
          || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0)
        );
        setUsers(combined.slice(0, 20));
      } catch (err) {
        if (cancelled) return;
        setUsers([]);
        setError("Could not load the rankings. Please try again.");
        console.error("Error fetching leaderboard:", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchLeaderboard();
    const refresh = () => fetchLeaderboard();
    window.addEventListener("focus", refresh);
    return () => {
      cancelled = true;
      window.removeEventListener("focus", refresh);
    };
  }, [activeCategory]);

  return (
    <div className={styles.leaderPage}>
      <PageShapes page="leaderboard" />
      <div className="container" style={{ position: "relative", zIndex: 1 }}>
        
        <header className={styles.leaderHeader}>
          <ScrollReveal animation="fadeUp">
            <h1>Leaderboards</h1>
            <p>Celebrating the most dedicated writers in our community.</p>
          </ScrollReveal>
        </header>

        {/* Tab Selection */}
        <ScrollReveal animation="fadeUp" delay={100}>
          <div className={styles.tabs}>
            {CATEGORIES.map(cat => (
              <button 
                key={cat.id} 
                className={`${styles.tab} ${activeCategory.id === cat.id ? styles.active : ""}`}
                onClick={() => setActiveCategory(cat)}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </ScrollReveal>

        <div className={styles.leaderList}>
          {error ? <p role="alert">{error}</p> : loading ? (
            <div className="spinner" style={{ margin: "50px auto" }} />
          ) : users.length > 0 ? (
            users.map((u, i) => {
              const actualRank = i + 1;
              let rankClass = "";
              if (actualRank === 1) rankClass = styles.rank1;
              else if (actualRank === 2) rankClass = styles.rank2;
              else if (actualRank === 3) rankClass = styles.rank3;
              
              return (
                <ScrollReveal key={u.id} animation="slideLeft" delay={10 + (i * 30)}>
                  <div className={`${styles.leaderItem} ${rankClass}`}>
                    <div className={styles.leaderRank}>{actualRank}</div>
                    
                    <div className={styles.leaderInfo}>
                      <div className={styles.leaderAvatar}>
                        {(u.username || "U")[0].toUpperCase()}
                      </div>
                      <div className={styles.leaderName}>
                        <Link href={`/profile/${encodeURIComponent(u.username)}`} className={`username-custom username-color-${u.profile_color || "derby"}`}>@{u.username}</Link>
                      </div>
                    </div>

                    <div className={styles.leaderValue}>
                      {(u[activeCategory.sortKey] || 0).toLocaleString()} 
                      <div className={styles.leaderSubLabel}>{activeCategory.unit}</div>
                    </div>
                  </div>
                </ScrollReveal>
              );
            })
          ) : (
            <div style={{ textAlign: "center", padding: "100px", color: "var(--text-muted)" }}>
              <p>No writers on the board yet. Start a sprint to be the first!</p>
            </div>
          )}
        </div>
        
      </div>
    </div>
  );
}
