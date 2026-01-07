/**
 * Validation Error Display Component
 * Displays field-level validation errors from API responses
 */
import './ValidationErrorDisplay.css';

interface ValidationError {
  field: string;
  message: string;
  type?: string;
}

interface ValidationErrorDisplayProps {
  errors?: ValidationError[];
  className?: string;
}

/**
 * Component to display validation errors
 */
export const ValidationErrorDisplay = ({ 
  errors, 
  className = '' 
}: ValidationErrorDisplayProps) => {
  if (!errors || errors.length === 0) {
    return null;
  }

  return (
    <div className={`validation-error-display ${className}`}>
      <div className="validation-error-header">
        <span className="validation-error-icon">⚠️</span>
        <span className="validation-error-title">Please fix the following errors:</span>
      </div>
      <ul className="validation-error-list">
        {errors.map((error, index) => (
          <li key={index} className="validation-error-item">
            <span className="validation-error-field">
              {error.field || 'Field'}:
            </span>
            <span className="validation-error-message">{error.message}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

/**
 * Inline field error display
 */
export const FieldError = ({ 
  error, 
  className = '' 
}: { 
  error?: string; 
  className?: string;
}) => {
  if (!error) {
    return null;
  }

  return (
    <div className={`field-error ${className}`}>
      <span className="field-error-icon">⚠️</span>
      <span className="field-error-text">{error}</span>
    </div>
  );
};

export default ValidationErrorDisplay;






