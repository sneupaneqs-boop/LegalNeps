import Link from "next/link";

export default function NotFound() {
  return (
    <div className="page">
      <div className="empty-state" style={{ marginTop: 80 }}>
        <p>Not found.</p>
        <Link className="nav-link" href="/search">
          ← Back to search
        </Link>
      </div>
    </div>
  );
}
