import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="not-found-page">
      <span className="not-found-code">404</span>

      <h1>Page not found</h1>

      <p>The page you're looking for doesn't exist.</p>

      <Link to="/" className="hero-button">
        Return to dashboard
      </Link>
    </div>
  );
}