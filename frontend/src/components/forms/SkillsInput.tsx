/**
 * SkillsInput Component
 * Tag input component for skills with validation
 */
import { useState, KeyboardEvent } from 'react';
import { UseFormRegisterReturn, FieldError } from 'react-hook-form';
import './SkillsInput.css';

interface SkillsInputProps {
  skills: string[];
  onSkillsChange: (skills: string[]) => void;
  register?: UseFormRegisterReturn;
  error?: FieldError;
  placeholder?: string;
  maxSkills?: number;
}

export function SkillsInput({
  skills,
  onSkillsChange,
  register,
  error,
  placeholder = 'Type a skill and press Enter',
  maxSkills,
}: SkillsInputProps): JSX.Element {
  const [inputValue, setInputValue] = useState<string>('');

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      const trimmedSkill = inputValue.trim();
      
      // Validate skill length
      if (trimmedSkill.length > 100) {
        return; // Will be caught by validation
      }

      // Check if skill already exists (case-insensitive)
      if (!skills.some(skill => skill.toLowerCase() === trimmedSkill.toLowerCase())) {
        // Check max skills limit
        if (maxSkills && skills.length >= maxSkills) {
          return;
        }
        onSkillsChange([...skills, trimmedSkill]);
        setInputValue('');
      }
    } else if (e.key === 'Backspace' && inputValue === '' && skills.length > 0) {
      // Remove last skill when backspace is pressed on empty input
      onSkillsChange(skills.slice(0, -1));
    }
  };

  const removeSkill = (skillToRemove: string): void => {
    onSkillsChange(skills.filter(skill => skill !== skillToRemove));
  };

  return (
    <div className="skills-input-container">
      <div className="skill-input-wrapper">
        <input
          type="text"
          className={`skill-input ${error ? 'error' : ''}`}
          placeholder={placeholder}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          {...register}
        />
        {maxSkills && (
          <span className="skill-count">
            {skills.length}/{maxSkills}
          </span>
        )}
      </div>
      {skills.length > 0 && (
        <div className="skills-list">
          {skills.map((skill, index) => (
            <span key={index} className="skill-tag">
              {skill}
              <button
                type="button"
                className="skill-remove"
                onClick={() => removeSkill(skill)}
                aria-label={`Remove ${skill}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      {error && <span className="form-error">{error.message}</span>}
    </div>
  );
}

export default SkillsInput;




