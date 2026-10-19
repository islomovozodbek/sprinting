"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import PageShapes from "@/components/PageShapes";

export default function ReferralPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading || !user) {
    return (
      <div style={{ padding: "var(--space-4xl) 0", textAlign: "center" }}>
        <div className="spinner spinner-lg mx-auto" />
      </div>
    );
  }

  const referralLink = `https://sprinting.ink/register?ref=${encodeURIComponent(user.referralCode || "")}`;

  const copyLink = () => {
    navigator.clipboard.writeText(referralLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ padding: "var(--space-2xl) 0", minHeight: "calc(100vh - var(--nav-height))", position: "relative", overflow: "hidden" }}>
      <PageShapes page="referral" />
      <div className="container" style={{ maxWidth: "600px", position: "relative", zIndex: 1 }}>
        <div className="text-center" style={{ marginBottom: "var(--space-2xl)" }}>
          <h1 style={{ marginBottom: "var(--space-sm)" }}>Invite a Friend</h1>
          <p className="text-muted">
            Share Sprinting Ink with friends and build a writing habit together.
          </p>
        </div>

        {/* Your referral link */}
        <div className="card" style={{ marginBottom: "var(--space-xl)", textAlign: "center" }}>
          <h3 style={{ marginBottom: "var(--space-md)" }}>Your Invite Link</h3>
          <div style={{
            display: "flex",
            gap: "var(--space-sm)",
            alignItems: "center",
            background: "var(--bg-secondary)",
            borderRadius: "var(--radius-md)",
            padding: "var(--space-sm)",
          }}>
            <input
              type="text"
              className="input"
              value={referralLink}
              readOnly
              style={{ flex: 1, fontSize: "0.85rem", border: "none", background: "transparent" }}
            />
            <button className="btn btn-primary btn-sm" onClick={copyLink}>
              {copied ? "Copied! ✓" : "Copy"}
            </button>
          </div>
          <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "var(--space-md)" }}>
            Friends referred so far: <strong>{user.referralCount || 0}</strong>
          </p>
        </div>

        {/* How it works */}
        <div className="card-flat" style={{ padding: "var(--space-xl)", borderRadius: "var(--radius-lg)" }}>
          <h4 style={{ marginBottom: "var(--space-md)" }}>How it works</h4>
          <ol style={{ paddingLeft: "var(--space-lg)", display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
            <li style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              Share your unique referral link with friends
            </li>
            <li style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              Your friends can create a free account and start writing right away.
            </li>
            <li style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              Try a daily prompt together and read each other&apos;s stories.
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
