import { useNavigate } from 'react-router-dom';
import './NotFoundPage.css';

/**
 * NotFoundPage Component
 * 404 error page displayed when a route is not found
 */
function NotFoundPage(): JSX.Element {
  const navigate = useNavigate();

  return (
    <div className="not-found-page">
      <div className="not-found-container">
        <h1 className="not-found-code">404</h1>
        <h2 className="not-found-title">Page Not Found</h2>
        <p className="not-found-message">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="not-found-actions">
          <button 
            className="not-found-button primary" 
            onClick={() => navigate('/')}
          >
            Go to Home
          </button>
          <button 
            className="not-found-button secondary" 
            onClick={() => navigate(-1)}
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
}

export default NotFoundPage;






