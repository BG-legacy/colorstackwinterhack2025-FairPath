import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './ResumePage.css';
import resumeService, {
  ResumeAnalysisResponse,
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

  // Target career state (for analysis)
  const [targetCareerName, setTargetCareerName] = useState<string>('');
  const [validatedCareer, setValidatedCareer] = useState<{ career_id: string; name: string } | null>(null);
  const [isValidatingCareer, setIsValidatingCareer] = useState<boolean>(false);
  const [careerValidationError, setCareerValidationError] = useState<string>('');

  // Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string>('');
  const [analysisResults, setAnalysisResults] = useState<ResumeAnalysisResponse | null>(null);
  const [showExtractedText, setShowExtractedText] = useState<boolean>(false);

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

  // Validate career name with debounce (for analysis)
  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (!targetCareerName.trim()) {
        setValidatedCareer(null);
        setCareerValidationError('');
        return;
      }

      setIsValidatingCareer(true);
      setCareerValidationError('');
      try {
        const validated = await dataService.validateCareerName(targetCareerName);
        if (validated) {
          setValidatedCareer({
            career_id: validated.career_id,
            name: validated.name
          });
          setCareerValidationError('');
        } else {
          setValidatedCareer(null);
          setCareerValidationError('No matching career found. Please try a different name.');
        }
      } catch (err) {
        setValidatedCareer(null);
        setCareerValidationError(err instanceof Error ? err.message : 'Failed to validate career name');
      } finally {
        setIsValidatingCareer(false);
      }
    }, 800); // Debounce delay for validation
    return () => clearTimeout(timeoutId);
  }, [targetCareerName]);

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

  // Handle file selection
  const handleFileSelect = useCallback((file: File): void => {
    setFileError('');
    const validationError = validateFile(file);
    if (validationError) {
      setFileError(validationError.message);
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
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

  // Handle analysis
  const handleAnalyze = async (): Promise<void> => {
    if (!selectedFile) {
      setFileError('Please select a file first');
      return;
    }

    setAnalysisError('');
    setIsAnalyzing(true);
    setAnalysisResults(null);

    try {
      const result = await resumeService.analyzeResume(
        selectedFile,
        validatedCareer?.career_id,
        validatedCareer ? undefined : targetCareerName || undefined
      );
      setAnalysisResults(result);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Failed to analyze resume');
    } finally {
      setIsAnalyzing(false);
    }
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
          <h1 className="resume-title">Resume Analysis & Rewrite</h1>

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
                      setAnalysisResults(null);
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

            {/* Target Career Input (Optional) */}
            <div className="target-career-selector">
              <label className="form-label">Target Career (Optional - for gap analysis)</label>
              <input
                type="text"
                className="form-input"
                placeholder="Type a career name or description (e.g., 'Software Engineer', 'Data Scientist')..."
                value={targetCareerName}
                onChange={(e) => {
                  setTargetCareerName(e.target.value);
                  if (!e.target.value) {
                    setValidatedCareer(null);
                    setCareerValidationError('');
                  }
                }}
              />
              {isValidatingCareer && (
                <div className="search-loading">Validating career with AI...</div>
              )}
              {validatedCareer && !isValidatingCareer && targetCareerName.trim() && (
                <div className="selected-career" style={{ marginTop: '8px', color: '#4CAF50' }}>
                  <span>✓ Using: {targetCareerName}</span>
                </div>
              )}
              {careerValidationError && !isValidatingCareer && (
                <div className="error-message" style={{ marginTop: '8px' }}>{careerValidationError}</div>
              )}
            </div>

            <button
              type="button"
              className="submit-button"
              onClick={handleAnalyze}
              disabled={!selectedFile || isAnalyzing}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Resume'}
            </button>
            {analysisError && <div className="error-banner">{analysisError}</div>}
          </div>

          {/* Analysis Results */}
          {analysisResults && (
            <div className="analysis-results">
              <h2 className="section-title">Analysis Results</h2>

              {/* Extracted Text (Collapsible) */}
              <div className="result-section">
                <button
                  type="button"
                  className="collapsible-header"
                  onClick={() => setShowExtractedText(!showExtractedText)}
                >
                  <span>Extracted Text</span>
                  <span className="collapsible-icon">{showExtractedText ? '▼' : '▶'}</span>
                </button>
                {showExtractedText && (
                  <div className="collapsible-content">
                    <pre className="extracted-text">{analysisResults.extracted_text}</pre>
                  </div>
                )}
              </div>

              {/* Detected Skills */}
              <div className="result-section">
                <h3 className="subsection-title">Detected Skills ({analysisResults.detected_skills.length})</h3>
                <div className="skills-grid">
                  {analysisResults.detected_skills.map((skill, index) => (
                    <div key={index} className="skill-item">
                      <span className="skill-name">{skill.skill}</span>
                      {skill.confidence !== undefined && (
                        <span className="skill-confidence">
                          {(skill.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Resume Structure */}
              <div className="result-section">
                <h3 className="subsection-title">Resume Structure</h3>
                {analysisResults.structure.sections && analysisResults.structure.sections.length > 0 && (
                  <div className="structure-section">
                    <h4 className="structure-title">Sections:</h4>
                    <ul className="structure-list">
                      {analysisResults.structure.sections.map((section, index) => (
                        <li key={index}>{section}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {analysisResults.structure.bullets && analysisResults.structure.bullets.length > 0 && (
                  <div className="structure-section">
                    <h4 className="structure-title">Bullet Points ({analysisResults.structure.bullets.length}):</h4>
                    <ul className="structure-list">
                      {analysisResults.structure.bullets.map((bullet, index) => (
                        <li key={index}>{bullet}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Gap Analysis - Only show if there's a good match */}
              {analysisResults.gap_analysis && 
               !analysisResults.gap_analysis.error && 
               (!analysisResults.gap_analysis.is_poor_match || (analysisResults.gap_analysis.coverage_percentage !== undefined && analysisResults.gap_analysis.coverage_percentage > 0)) && (
                <div className="result-section">
                  <h3 className="subsection-title">Gap Analysis</h3>
                  <>
                    {analysisResults.gap_analysis.target_career && (
                      <div className="gap-section">
                        <p className="gap-info">
                          {analysisResults.gap_analysis.target_career.user_input && 
                           analysisResults.gap_analysis.target_career.user_input !== analysisResults.gap_analysis.target_career.name ? (
                            <>
                              Analyzing gaps for: <strong>{analysisResults.gap_analysis.target_career.name}</strong>
                              <span className="matched-from" style={{ fontSize: '0.9em', color: '#666', marginLeft: '8px' }}>
                                (matched from "{analysisResults.gap_analysis.target_career.user_input}")
                              </span>
                            </>
                          ) : (
                            <>
                              Analyzing gaps for: <strong>{analysisResults.gap_analysis.target_career.name}</strong>
                            </>
                          )}
                          {analysisResults.gap_analysis.coverage_percentage !== undefined && 
                           analysisResults.gap_analysis.coverage_percentage > 0 && (
                            <span className="coverage-badge">
                              {analysisResults.gap_analysis.coverage_percentage.toFixed(1)}% coverage
                            </span>
                          )}
                        </p>
                        {analysisResults.gap_analysis.analysis_explanation && (
                          <div className="gap-explanation">
                            <p>{analysisResults.gap_analysis.analysis_explanation}</p>
                          </div>
                        )}
                      </div>
                    )}
                    {analysisResults.gap_analysis.missing_important_skills && analysisResults.gap_analysis.missing_important_skills.length > 0 && (
                      <div className="gap-section">
                        <h4 className="gap-title">Missing Important Skills (High Priority):</h4>
                        <div className="skills-grid">
                          {analysisResults.gap_analysis.missing_important_skills.map((skill, index) => (
                            <div key={index} className="skill-item missing important">
                              {skill}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {analysisResults.gap_analysis.missing_skills && analysisResults.gap_analysis.missing_skills.length > 0 && (
                      <div className="gap-section">
                        <h4 className="gap-title">Other Missing Skills:</h4>
                        <div className="skills-grid">
                          {analysisResults.gap_analysis.missing_skills.map((skill, index) => (
                            <div key={index} className="skill-item missing">
                              {skill}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                      {analysisResults.gap_analysis.matching_skills && analysisResults.gap_analysis.matching_skills.length > 0 && (
                        <div className="gap-section">
                          <h4 className="gap-title">Matching Skills:</h4>
                          <div className="skills-grid">
                            {analysisResults.gap_analysis.matching_skills.map((skill, index) => (
                              <div key={index} className="skill-item matching">
                                {skill}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {analysisResults.gap_analysis.recommended_skills && analysisResults.gap_analysis.recommended_skills.length > 0 && (
                        <div className="gap-section">
                          <h4 className="gap-title">Recommended Skills:</h4>
                          <div className="skills-grid">
                            {analysisResults.gap_analysis.recommended_skills.map((skill, index) => (
                              <div key={index} className="skill-item recommended">
                                {skill}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {analysisResults.gap_analysis.skill_gaps && analysisResults.gap_analysis.skill_gaps.length > 0 && (
                        <div className="gap-section">
                          <h4 className="gap-title">Detailed Skill Gaps:</h4>
                          <ul className="gap-list">
                            {analysisResults.gap_analysis.skill_gaps.map((gap, index) => (
                              <li key={index} className={`gap-item ${gap.gap_level}`}>
                                <div className="gap-item-content">
                                  <span className="gap-skill">{gap.skill}</span>
                                  <span className="gap-importance">Importance: {gap.importance.toFixed(1)}</span>
                                  <span className={`gap-level ${gap.gap_level}`}>{gap.gap_level}</span>
                                </div>
                                {gap.explanation && (
                                  <p className="gap-explanation-text">{gap.explanation}</p>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    {(!analysisResults.gap_analysis.missing_important_skills || analysisResults.gap_analysis.missing_important_skills.length === 0) &&
                     (!analysisResults.gap_analysis.missing_skills || analysisResults.gap_analysis.missing_skills.length === 0) &&
                     (analysisResults.gap_analysis.coverage_percentage !== undefined && analysisResults.gap_analysis.coverage_percentage > 0) && (
                      <div className="gap-section">
                        <p className="gap-info">No significant skill gaps identified. Your resume skills align well with the target career!</p>
                      </div>
                    )}
                  </>
                </div>
              )}
              {/* Show error message if gap analysis failed or is a poor match */}
              {analysisResults.gap_analysis && 
               analysisResults.gap_analysis.error && (
                <div className="result-section">
                  <h3 className="subsection-title">Gap Analysis</h3>
                  <div className="error-message">{analysisResults.gap_analysis.error}</div>
                </div>
              )}
              {analysisResults.gap_analysis && 
               !analysisResults.gap_analysis.error && 
               analysisResults.gap_analysis.is_poor_match && 
               (analysisResults.gap_analysis.coverage_percentage === undefined || analysisResults.gap_analysis.coverage_percentage === 0) && (
                <div className="result-section">
                  <h3 className="subsection-title">Gap Analysis</h3>
                  <div className="error-message" style={{ color: '#666' }}>
                    Unable to perform gap analysis: No matching skills found between your resume and the target career. 
                    This may indicate the target career requires different skills than what's currently in your resume, 
                    or the career match may need adjustment.
                  </div>
                </div>
              )}
            </div>
          )}

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

