/**
 * Progress Indicator Components
 * For long-running requests and file uploads
 */
import { useEffect, useState } from 'react';
import './ProgressIndicator.css';

interface ProgressIndicatorProps {
  message?: string;
  progress?: number; // 0-100
  indeterminate?: boolean;
  showPercentage?: boolean;
}

/**
 * Linear progress bar
 */
export const LinearProgress = ({
  message = 'Loading...',
  progress,
  indeterminate = false,
  showPercentage = false,
}: ProgressIndicatorProps) => {
  const [animatedProgress, setAnimatedProgress] = useState(0);

  useEffect(() => {
    if (indeterminate) {
      // Animate indeterminate progress
      const interval = setInterval(() => {
        setAnimatedProgress((prev) => (prev + 2) % 100);
      }, 50);
      return () => clearInterval(interval);
    } else if (progress !== undefined) {
      // Animate to target progress
      const duration = 300;
      const steps = 30;
      const increment = (progress - animatedProgress) / steps;
      let current = animatedProgress;
      
      const interval = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= progress) || (increment < 0 && current <= progress)) {
          setAnimatedProgress(progress);
          clearInterval(interval);
        } else {
          setAnimatedProgress(current);
        }
      }, duration / steps);
      
      return () => clearInterval(interval);
    }
  }, [progress, indeterminate]);

  const displayProgress = indeterminate ? animatedProgress : (progress ?? 0);

  return (
    <div className="linear-progress-container">
      {message && <div className="progress-message">{message}</div>}
      <div className="linear-progress-wrapper">
        <div
          className={`linear-progress-bar ${indeterminate ? 'indeterminate' : ''}`}
          style={{
            width: indeterminate ? '100%' : `${displayProgress}%`,
          }}
        />
      </div>
      {showPercentage && !indeterminate && (
        <div className="progress-percentage">{Math.round(displayProgress)}%</div>
      )}
    </div>
  );
};

/**
 * Circular progress spinner
 */
export const CircularProgress = ({
  message,
  size = 48,
  strokeWidth = 4,
}: {
  message?: string;
  size?: number;
  strokeWidth?: number;
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Animate the circle
    const interval = setInterval(() => {
      setProgress((prev) => (prev + 2) % 100);
    }, 20);
    return () => clearInterval(interval);
  }, []);

  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className="circular-progress-container">
      <svg
        className="circular-progress"
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
      >
        <circle
          className="circular-progress-background"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
        <circle
          className="circular-progress-foreground"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      {message && <div className="progress-message">{message}</div>}
    </div>
  );
};

/**
 * Dots loading indicator
 */
export const DotsLoader = ({ message }: { message?: string }) => {
  return (
    <div className="dots-loader-container">
      <div className="dots-loader">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
      {message && <div className="progress-message">{message}</div>}
    </div>
  );
};

/**
 * Full-page loading overlay
 */
export const LoadingOverlay = ({
  message = 'Loading...',
  progress,
  indeterminate = true,
}: ProgressIndicatorProps) => {
  return (
    <div className="loading-overlay">
      <div className="loading-overlay-content">
        <CircularProgress message={message} size={64} />
        {progress !== undefined && (
          <LinearProgress
            progress={progress}
            indeterminate={indeterminate}
            showPercentage={true}
          />
        )}
      </div>
    </div>
  );
};

export default LinearProgress;






