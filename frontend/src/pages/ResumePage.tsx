import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './ResumePage.css';
import resumeService, {
  ResumeRewriteRequest,
  ResumeRewriteResponse,
  validateFile,
  MAX_FILE_SIZE,
} from '../services/resume';
import dataService from '../services/data';

interface Particle {
  x: number;
  y: number;
  size: number;
  opacity: number;
  speed: number;
}

function ResumePage(): JSX.Element {
  const navigate = useNavigate();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  // File upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [fileError, setFileError] = useState<string>('');
  const [isExtracting, setIsExtracting] = useState<boolean>(false);

  // Rewrite state
  const [rewriteBullets, setRewriteBullets] = useState<string[]>(['']);
  const [rewriteTargetCareerName, setRewriteTargetCareerName] = useState<string>('');
  const [rewriteValidatedCareer, setRewriteValidatedCareer] = useState<{ career_id: string; name: string } | null>(null);
  const [isValidatingRewriteCareer, setIsValidatingRewriteCareer] = useState<boolean>(false);
  const [rewriteCareerValidationError, setRewriteCareerValidationError] = useState<string>('');
  const [rewriteResumeText, setRewriteResumeText] = useState<string>('');
  const [isRewriting, setIsRewriting] = useState<boolean>(false);
  const [rewriteError, setRewriteError] = useState<string>('');
  const [rewriteResults, setRewriteResults] = useState<ResumeRewriteResponse | null>(null);

  // Validate career name with debounce (for rewrite)
  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (!rewriteTargetCareerName.trim()) {
        setRewriteValidatedCareer(null);
        setRewriteCareerValidationError('');
        return;
      }

      setIsValidatingRewriteCareer(true);
      setRewriteCareerValidationError('');
      try {
        const validated = await dataService.validateCareerName(rewriteTargetCareerName);
        if (validated) {
          setRewriteValidatedCareer({
            career_id: validated.career_id,
            name: validated.name
          });
          setRewriteCareerValidationError('');
        } else {
          setRewriteValidatedCareer(null);
          setRewriteCareerValidationError('No matching career found. Please try a different name.');
        }
      } catch (err) {
        setRewriteValidatedCareer(null);
        setRewriteCareerValidationError(err instanceof Error ? err.message : 'Failed to validate career name');
      } finally {
        setIsValidatingRewriteCareer(false);
      }
    }, 800); // Debounce delay for validation
    return () => clearTimeout(timeoutId);
  }, [rewriteTargetCareerName]);

  // Handle file selection - automatically extract text and bullets
  const handleFileSelect = useCallback(async (file: File): Promise<void> => {
    setFileError('');
    const validationError = validateFile(file);
    if (validationError) {
      setFileError(validationError.message);
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
    
    // Automatically extract text and bullets from the resume
    setIsExtracting(true);
    setFileError('');
    try {
      const result = await resumeService.analyzeResume(file);
      
      // Populate rewrite section with extracted data
      if (result.structure.bullets && result.structure.bullets.length > 0) {
        setRewriteBullets(result.structure.bullets);
      } else {
        // If no bullets found, keep at least one empty field
        setRewriteBullets(['']);
      }
      
      // Set the full resume text for context
      if (result.extracted_text) {
        setRewriteResumeText(result.extracted_text);
      }
    } catch (err) {
      setFileError(err instanceof Error ? err.message : 'Failed to extract resume content');
    } finally {
      setIsExtracting(false);
    }
  }, []);

  // Handle file input change
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // Handle drag and drop
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // Handle file picker button click
  const handleFilePickerClick = (): void => {
    fileInputRef.current?.click();
  };

  // Handle rewrite
  const handleRewrite = async (): Promise<void> => {
    const validBullets = rewriteBullets.filter(b => b.trim().length > 0);
    if (validBullets.length === 0) {
      setRewriteError('Please provide at least one bullet point');
      return;
    }

    if (!rewriteTargetCareerName.trim()) {
      setRewriteError('Please enter a target career');
      return;
    }

    setRewriteError('');
    setIsRewriting(true);
    setRewriteResults(null);

    try {
      const request: ResumeRewriteRequest = {
        bullets: validBullets,
        target_career_id: rewriteValidatedCareer?.career_id,
        target_career_name: rewriteTargetCareerName.trim(), // Always use user's exact input
        resume_text: rewriteResumeText.trim() || undefined,
      };

      const result = await resumeService.rewriteResumeBullets(request);
      setRewriteResults(result);
    } catch (err) {
      setRewriteError(err instanceof Error ? err.message : 'Failed to rewrite bullets');
    } finally {
      setIsRewriting(false);
    }
  };

  // Add/remove bullet points
  const addBulletPoint = (): void => {
    setRewriteBullets([...rewriteBullets, '']);
  };

  const removeBulletPoint = (index: number): void => {
    if (rewriteBullets.length > 1) {
      setRewriteBullets(rewriteBullets.filter((_, i) => i !== index));
    }
  };

  const updateBulletPoint = (index: number, value: string): void => {
    const updated = [...rewriteBullets];
    updated[index] = value;
    setRewriteBullets(updated);
  };

  // Canvas animation
  useEffect(() => {
    const canvas: HTMLCanvasElement | null = canvasRef.current;
    if (!canvas) return;

    const ctx: CanvasRenderingContext2D | null = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = (): void => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const particles: Particle[] = [];
    const isMobile: boolean = window.innerWidth < 768;
    const particleCount: number = isMobile
      ? Math.min(Math.floor(window.innerWidth * 0.1), 50)
      : Math.min(window.innerWidth * 0.15, 100);

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2 + 0.5,
        opacity: Math.random(),
        speed: Math.random() * 0.5 + 0.1,
      });
    }

    const animate = (): void => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((particle: Particle) => {
        particle.opacity += Math.sin(Date.now() * 0.001 + particle.x) * 0.01;
        particle.opacity = Math.max(0.2, Math.min(1, particle.opacity));

        ctx.beginPath();
        ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();
      });

      requestAnimationFrame(animate);
    };

    animate();

    return (): void => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="resume-page">
      <canvas ref={canvasRef} className="particles-canvas" />
      <div className="resume-container">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Back to Home
        </button>

        <div className="resume-content">
          <h1 className="resume-title">Resume Rewrite</h1>

          {/* File Upload Section */}
          <div className="upload-section">
            <h2 className="section-title">Upload Resume</h2>
            <div
              ref={dropZoneRef}
              className={`drop-zone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileInputChange}
                style={{ display: 'none' }}
              />
              {selectedFile ? (
                <div className="file-preview">
                  <div className="file-info">
                    <span className="file-name">{selectedFile.name}</span>
                    <span className="file-size">{formatFileSize(selectedFile.size)}</span>
                  </div>
                  <button
                    type="button"
                    className="file-remove"
                    onClick={() => {
                      setSelectedFile(null);
                      setFileError('');
                      setRewriteBullets(['']);
                      setRewriteResumeText('');
                    }}
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div className="drop-zone-content">
                  <div className="drop-zone-icon">📄</div>
                  <p className="drop-zone-text">Drag & drop your resume here</p>
                  <p className="drop-zone-subtext">or</p>
                  <button
                    type="button"
                    className="file-picker-button"
                    onClick={handleFilePickerClick}
                  >
                    Choose File
                  </button>
                  <p className="file-types">Supported: PDF, DOCX, TXT (Max {formatFileSize(MAX_FILE_SIZE)})</p>
                </div>
              )}
            </div>
            {fileError && <div className="error-message">{fileError}</div>}
            {isExtracting && (
              <div className="extracting-message" style={{ marginTop: '12px', color: '#666', fontStyle: 'italic' }}>
                Extracting resume content...
              </div>
            )}
          </div>

          {/* Rewrite Section */}
          <div className="rewrite-section">
            <h2 className="section-title">Rewrite Resume Bullets</h2>

            {/* Bullet Points Input */}
            <div className="bullets-input">
              <label className="form-label">Bullet Points to Rewrite</label>
              {rewriteBullets.map((bullet, index) => (
                <div key={index} className="bullet-input-row">
                  <textarea
                    className="form-textarea bullet-textarea"
                    placeholder="Enter a bullet point..."
                    value={bullet}
                    onChange={(e) => updateBulletPoint(index, e.target.value)}
                    rows={2}
                  />
                  {rewriteBullets.length > 1 && (
                    <button
                      type="button"
                      className="remove-bullet-button"
                      onClick={() => removeBulletPoint(index)}
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                className="add-bullet-button"
                onClick={addBulletPoint}
              >
                + Add Bullet Point
              </button>
            </div>

            {/* Target Career Input */}
            <div className="rewrite-target-career">
              <label className="form-label">Target Career *</label>
              <input
                type="text"
                className="form-input"
                placeholder="Type a career name or description (e.g., 'Business Analyst', 'Software Engineer')..."
                value={rewriteTargetCareerName}
                onChange={(e) => {
                  setRewriteTargetCareerName(e.target.value);
                  if (!e.target.value) {
                    setRewriteValidatedCareer(null);
                    setRewriteCareerValidationError('');
                  }
                }}
              />
              {isValidatingRewriteCareer && (
                <div className="search-loading">Validating career with AI...</div>
              )}
              {rewriteValidatedCareer && !isValidatingRewriteCareer && rewriteTargetCareerName.trim() && (
                <div className="selected-career" style={{ marginTop: '8px', color: '#4CAF50' }}>
                  <span>✓ Using: {rewriteTargetCareerName}</span>
                </div>
              )}
              {rewriteCareerValidationError && !isValidatingRewriteCareer && (
                <div className="error-message" style={{ marginTop: '8px' }}>{rewriteCareerValidationError}</div>
              )}
              <div className="form-hint" style={{ marginTop: '4px', fontSize: '0.875rem', color: '#666' }}>
                Your exact input will be used for rewriting.
              </div>
            </div>

            {/* Optional Full Resume Text */}
            <div className="rewrite-context">
              <label className="form-label">Full Resume Text (Optional - for context)</label>
              <textarea
                className="form-textarea"
                placeholder="Paste full resume text for better context..."
                value={rewriteResumeText}
                onChange={(e) => setRewriteResumeText(e.target.value)}
                rows={6}
              />
            </div>

            <button
              type="button"
              className="submit-button"
              onClick={handleRewrite}
              disabled={isRewriting}
            >
              {isRewriting ? 'Rewriting...' : 'Rewrite Bullets'}
            </button>
            {rewriteError && <div className="error-banner">{rewriteError}</div>}

            {/* Rewrite Results */}
            {rewriteResults && (
              <div className="rewrite-results">
                <h3 className="subsection-title">Rewritten Bullets</h3>
                <div className="target-career-info">
                  <strong>Target Career:</strong> {rewriteResults.target_career.name}
                </div>
                <div className="rewrites-list">
                  {rewriteResults.rewrites.map((rewrite, index) => (
                    <div key={index} className="rewrite-item">
                      <div className="rewrite-original">
                        <h4 className="rewrite-label">Original:</h4>
                        <p>{rewrite.original}</p>
                      </div>
                      <div className="rewrite-rewritten">
                        <h4 className="rewrite-label">Rewritten:</h4>
                        <p>{rewrite.rewritten}</p>
                      </div>
                      {rewrite.explanation && (
                        <div className="rewrite-explanation">
                          <h4 className="rewrite-label">Explanation:</h4>
                          <p>{rewrite.explanation}</p>
                        </div>
                      )}
                      {rewrite.compliance_note && (
                        <div className="rewrite-compliance">
                          <h4 className="rewrite-label">Compliance Note:</h4>
                          <p>{rewrite.compliance_note}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResumePage;

