"use client";

import { useEffect } from "react";
import Link from "next/link";

// S14: error boundary for this route segment - without it, an unhandled
// render/data error anywhere under app/ replaces the whole page with
// Next.js's default (blank in production, a raw stack trace in dev) rather
// than a page that lets someone get back to a working part of the site.
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error(error);
  }, [error]);

  return (
    <div className="page">
      <div className="empty-state" style={{ marginTop: 80 }}>
        <p>Something went wrong on our side. Nothing you did caused this.</p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center", marginTop: 12 }}>
          <button className="nav-link" onClick={() => reset()}>
            Try again
          </button>
          <Link className="nav-link" href="/">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
