/**
 * ValueSlider Component
 * Slider component for work values (0-7 scale)
 */
import { FieldError } from 'react-hook-form';
import './ValueSlider.css';

interface ValueSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  error?: FieldError;
  showValue?: boolean;
  description?: string;
}

export function ValueSlider({
  label,
  value,
  onChange,
  min = 0,
  max = 7,
  step = 0.1,
  error,
  showValue = true,
  description,
}: ValueSliderProps): JSX.Element {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    onChange(Number(e.target.value));
  };

  return (
    <div className="value-slider-container">
      <label className="value-slider-label">
        <div className="value-slider-header">
          <span className="value-slider-name">{label}</span>
          {showValue && (
            <span className="value-slider-value">{value.toFixed(1)}</span>
          )}
        </div>
        {description && (
          <p className="value-slider-description">{description}</p>
        )}
        <div className="value-slider-wrapper">
          <input
            type="range"
            className={`value-slider ${error ? 'error' : ''}`}
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={handleChange}
          />
          <div className="value-slider-labels">
            <span className="value-slider-min">{min}</span>
            <span className="value-slider-max">{max}</span>
          </div>
        </div>
      </label>
      {error && <span className="form-error">{error.message}</span>}
    </div>
  );
}

export default ValueSlider;




