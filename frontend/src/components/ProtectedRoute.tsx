import { ReactElement } from 'react';
import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: ReactElement;
  isAuthenticated?: boolean;
  redirectTo?: string;
}

/**
 * ProtectedRoute Component
 * Wraps routes that require authentication
 * Redirects to specified route if user is not authenticated
 * 
 * Usage:
 * <Route path="/protected" element={
 *   <ProtectedRoute isAuthenticated={isLoggedIn}>
 *     <ProtectedPage />
 *   </ProtectedRoute>
 * } />
 */
function ProtectedRoute({ 
  children, 
  isAuthenticated = false,
  redirectTo = '/'
}: ProtectedRouteProps): ReactElement {
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  return children;
}

export default ProtectedRoute;




