"use client";

import { useEffect } from "react";

// S14: catches an error thrown from the root layout itself (error.tsx alone
// can't - it renders inside the layout, so a layout-level crash bypasses
// it). Must render its own <html>/<body> since the real root layout is
// what failed.
export default function GlobalError({
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
    <html lang="en">
      <body>
        <div style={{ textAlign: "center", marginTop: 80, fontFamily: "sans-serif" }}>
          <p>Something went wrong loading Kanooni Sathi. Please try again.</p>
          <button onClick={() => reset()} style={{ marginTop: 12 }}>
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
