import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './TrustPage.css';
import trustService, { TrustPanelData, ModelCardsData } from '../services/trust';

interface Particle {
  x: number;
  y: number;
  size: number;
  opacity: number;
  speed: number;
}

function TrustPage(): JSX.Element {
  const navigate = useNavigate();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // State
  const [trustPanel, setTrustPanel] = useState<TrustPanelData | null>(null);
  const [modelCards, setModelCards] = useState<ModelCardsData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'trust' | 'models'>('trust');

  // Load data
  useEffect(() => {
    const loadData = async (): Promise<void> => {
      setIsLoading(true);
      setError('');

      try {
        const [trustData, modelData] = await Promise.all([
          trustService.getTrustPanel(),
          trustService.getModelCards(),
        ]);
        setTrustPanel(trustData);
        setModelCards(modelData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load trust and transparency data');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

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

  return (
    <div className="trust-page">
      <canvas ref={canvasRef} className="particles-canvas" />
      <div className="trust-container">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Back to Home
        </button>

        <div className="trust-content">
          <h1 className="trust-title">Trust & Transparency</h1>

          {/* Tabs */}
          <div className="tabs">
            <button
              className={`tab-button ${activeTab === 'trust' ? 'active' : ''}`}
              onClick={() => setActiveTab('trust')}
            >
              Trust Panel
            </button>
            <button
              className={`tab-button ${activeTab === 'models' ? 'active' : ''}`}
              onClick={() => setActiveTab('models')}
            >
              Model Cards
            </button>
          </div>

          {/* Error */}
          {error && <div className="error-banner">{error}</div>}

          {/* Loading */}
          {isLoading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading trust and transparency information...</p>
            </div>
          )}

          {/* Trust Panel */}
          {!isLoading && activeTab === 'trust' && trustPanel && (
            <div className="trust-panel-content">
              {/* What is Collected */}
              <div className="trust-section">
                <h2 className="section-title">What is Collected</h2>
                <p className="section-description">{trustPanel.what_is_collected.description}</p>
                <div className="data-types-grid">
                  {trustPanel.what_is_collected.data_types.map((dataType, index) => (
                    <div key={index} className="data-type-card">
                      <h3 className="data-type-title">{dataType.type}</h3>
                      <p className="data-type-description">{dataType.description}</p>
                      <div className="data-type-details">
                        <div className="detail-item">
                          <span className="detail-label">Source:</span>
                          <span className="detail-value">{dataType.source}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Usage:</span>
                          <span className="detail-value">{dataType.usage}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {trustPanel.what_is_collected.note && (
                  <p className="section-note">{trustPanel.what_is_collected.note}</p>
                )}
              </div>

              {/* What is NOT Collected */}
              <div className="trust-section">
                <h2 className="section-title">What is NOT Collected</h2>
                
                <div className="not-collected-section">
                  <h3 className="subsection-title">Resumes</h3>
                  <p className="subsection-description">{trustPanel.what_is_not_collected.resumes.description}</p>
                  <ul className="details-list">
                    {trustPanel.what_is_not_collected.resumes.details.map((detail, index) => (
                      <li key={index}>{detail}</li>
                    ))}
                  </ul>
                  {trustPanel.what_is_not_collected.resumes.endpoints.length > 0 && (
                    <div className="endpoints-list">
                      <span className="endpoints-label">Affected Endpoints:</span>
                      {trustPanel.what_is_not_collected.resumes.endpoints.map((endpoint, index) => (
                        <code key={index} className="endpoint-code">{endpoint}</code>
                      ))}
                    </div>
                  )}
                </div>

                <div className="not-collected-section">
                  <h3 className="subsection-title">Personal Identifying Information</h3>
                  <p className="subsection-description">
                    {trustPanel.what_is_not_collected.personal_identifying_information.description}
                  </p>
                  <ul className="details-list">
                    {trustPanel.what_is_not_collected.personal_identifying_information.details.map((detail, index) => (
                      <li key={index}>{detail}</li>
                    ))}
                  </ul>
                </div>

                <div className="not-collected-section">
                  <h3 className="subsection-title">User Activity</h3>
                  <p className="subsection-description">
                    {trustPanel.what_is_not_collected.user_activity.description}
                  </p>
                  <ul className="details-list">
                    {trustPanel.what_is_not_collected.user_activity.details.map((detail, index) => (
                      <li key={index}>{detail}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Retention Policy */}
              <div className="trust-section">
                <h2 className="section-title">Retention Policies</h2>
                
                <div className="retention-section">
                  <h3 className="subsection-title">Resumes</h3>
                  <p className="retention-policy">{trustPanel.retention_policy.resumes.policy}</p>
                  <ul className="details-list">
                    {trustPanel.retention_policy.resumes.details.map((detail, index) => (
                      <li key={index}>{detail}</li>
                    ))}
                  </ul>
                </div>

                <div className="retention-section">
                  <h3 className="subsection-title">User Profile Data</h3>
                  <p className="retention-policy">{trustPanel.retention_policy.user_profile_data.policy}</p>
                  <ul className="details-list">
                    {trustPanel.retention_policy.user_profile_data.details.map((detail, index) => (
                      <li key={index}>{detail}</li>
                    ))}
                  </ul>
                  {trustPanel.retention_policy.user_profile_data.note && (
                    <p className="section-note">{trustPanel.retention_policy.user_profile_data.note}</p>
                  )}
                </div>
              </div>

              {/* Limitations */}
              <div className="trust-section">
                <h2 className="section-title">Limitations</h2>
                
                <div className="limitation-section">
                  <h3 className="subsection-title">Data Coverage</h3>
                  <p className="subsection-description">
                    {trustPanel.limitations.data_coverage.description}
                  </p>
                  <ul className="details-list">
                    {trustPanel.limitations.data_coverage.details.map((detail, index) => (
                      <li key={index}>{detail}</li>
                    ))}
                  </ul>
                </div>

                <div className="limitation-section">
                  <h3 className="subsection-title">Model Limitations</h3>
                  <p className="subsection-description">
                    {trustPanel.limitations.model_limitations.description}
                  </p>
                  <ul className="details-list">
                    {trustPanel.limitations.model_limitations.details.map((detail, index) => (
                      <li key={index}>{detail}</li>
                    ))}
                  </ul>
                </div>

                <div className="limitation-section">
                  <h3 className="subsection-title">Processing Limitations</h3>
                  <p className="subsection-description">
                    {trustPanel.limitations.processing_limitations.description}
                  </p>
                  <ul className="details-list">
                    {trustPanel.limitations.processing_limitations.details.map((detail, index) => (
                      <li key={index}>{detail}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Model Cards */}
          {!isLoading && activeTab === 'models' && modelCards && (
            <div className="model-cards-content">
              {/* Datasets Used */}
              <div className="model-section">
                <h2 className="section-title">Datasets Used</h2>
                
                <div className="dataset-card">
                  <h3 className="dataset-title">O*NET Database</h3>
                  <div className="dataset-info">
                    <div className="info-row">
                      <span className="info-label">Version:</span>
                      <span className="info-value">{modelCards.datasets_used.onet_database.version}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Release Date:</span>
                      <span className="info-value">{modelCards.datasets_used.onet_database.release_date}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Source:</span>
                      <span className="info-value">{modelCards.datasets_used.onet_database.source}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">License:</span>
                      <span className="info-value">{modelCards.datasets_used.onet_database.license}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Coverage:</span>
                      <span className="info-value">{modelCards.datasets_used.onet_database.coverage}</span>
                    </div>
                  </div>
                  <p className="dataset-description">{modelCards.datasets_used.onet_database.description}</p>
                  <div className="files-list">
                    <span className="files-label">Files Used:</span>
                    <ul>
                      {modelCards.datasets_used.onet_database.files_used.map((file, index) => (
                        <li key={index}>{file}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="dataset-card">
                  <h3 className="dataset-title">BLS Employment Projections</h3>
                  <div className="dataset-info">
                    <div className="info-row">
                      <span className="info-label">Version:</span>
                      <span className="info-value">{modelCards.datasets_used.bls_employment_projections.version}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Release Date:</span>
                      <span className="info-value">{modelCards.datasets_used.bls_employment_projections.release_date}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Source:</span>
                      <span className="info-value">{modelCards.datasets_used.bls_employment_projections.source}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">License:</span>
                      <span className="info-value">{modelCards.datasets_used.bls_employment_projections.license}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Coverage:</span>
                      <span className="info-value">{modelCards.datasets_used.bls_employment_projections.coverage}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Time Horizon:</span>
                      <span className="info-value">{modelCards.datasets_used.bls_employment_projections.time_horizon}</span>
                    </div>
                  </div>
                  <p className="dataset-description">{modelCards.datasets_used.bls_employment_projections.description}</p>
                  <div className="files-list">
                    <span className="files-label">Files Used:</span>
                    <ul>
                      {modelCards.datasets_used.bls_employment_projections.files_used.map((file, index) => (
                        <li key={index}>{file}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="dataset-card">
                  <h3 className="dataset-title">Training Data</h3>
                  <div className="dataset-info">
                    <div className="info-row">
                      <span className="info-label">Sample Size:</span>
                      <span className="info-value">{modelCards.datasets_used.training_data.sample_size}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Generation Method:</span>
                      <span className="info-value">{modelCards.datasets_used.training_data.generation_method}</span>
                    </div>
                  </div>
                  <p className="dataset-description">{modelCards.datasets_used.training_data.description}</p>
                  {modelCards.datasets_used.training_data.note && (
                    <p className="section-note">{modelCards.datasets_used.training_data.note}</p>
                  )}
                </div>
              </div>

              {/* Model Types */}
              <div className="model-section">
                <h2 className="section-title">Model Types</h2>
                
                <div className="model-card">
                  <h3 className="model-card-title">{modelCards.model_types.career_recommendation_model.name}</h3>
                  <div className="model-info">
                    <div className="info-row">
                      <span className="info-label">Type:</span>
                      <span className="info-value">{modelCards.model_types.career_recommendation_model.type}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Version:</span>
                      <span className="info-value">{modelCards.model_types.career_recommendation_model.version}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Library:</span>
                      <span className="info-value">{modelCards.model_types.career_recommendation_model.library}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Purpose:</span>
                      <span className="info-value">{modelCards.model_types.career_recommendation_model.purpose}</span>
                    </div>
                  </div>
                  <div className="architecture-section">
                    <h4 className="architecture-title">Architecture</h4>
                    <div className="architecture-grid">
                      {Object.entries(modelCards.model_types.career_recommendation_model.architecture).map(([key, value]) => (
                        <div key={key} className="architecture-item">
                          <span className="architecture-label">{key.replace(/_/g, ' ')}:</span>
                          <span className="architecture-value">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="input-features-section">
                    <h4 className="input-features-title">Input Features</h4>
                    <ul className="features-list">
                      {modelCards.model_types.career_recommendation_model.input_features.map((feature, index) => (
                        <li key={index}>{feature}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="output-section">
                    <span className="output-label">Output:</span>
                    <span className="output-value">{modelCards.model_types.career_recommendation_model.output}</span>
                  </div>
                </div>

                <div className="model-card">
                  <h3 className="model-card-title">{modelCards.model_types.baseline_model.name}</h3>
                  <div className="model-info">
                    <div className="info-row">
                      <span className="info-label">Type:</span>
                      <span className="info-value">{modelCards.model_types.baseline_model.type}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Algorithm:</span>
                      <span className="info-value">{modelCards.model_types.baseline_model.algorithm}</span>
                    </div>
                  </div>
                  <p className="model-description">{modelCards.model_types.baseline_model.description}</p>
                  <div className="usage-section">
                    <span className="usage-label">Usage:</span>
                    <span className="usage-value">{modelCards.model_types.baseline_model.usage}</span>
                  </div>
                </div>
              </div>

              {/* Evaluation Metrics */}
              <div className="model-section">
                <h2 className="section-title">Evaluation Metrics</h2>
                
                <div className="metrics-card">
                  <h3 className="metrics-title">Performance Metrics</h3>
                  <div className="metrics-grid">
                    {Object.entries(modelCards.evaluation_metrics.performance_metrics).map(([key, value]) => {
                      if (key === 'evaluation_note') return null;
                      return (
                        <div key={key} className="metric-item">
                          <span className="metric-label">{key.replace(/_/g, ' ')}:</span>
                          <span className="metric-value">{String(value)}</span>
                        </div>
                      );
                    })}
                  </div>
                  {modelCards.evaluation_metrics.performance_metrics.evaluation_note && (
                    <p className="section-note">
                      {modelCards.evaluation_metrics.performance_metrics.evaluation_note}
                    </p>
                  )}
                </div>

                <div className="metrics-card">
                  <h3 className="metrics-title">Test Set Details</h3>
                  <div className="metrics-grid">
                    {Object.entries(modelCards.evaluation_metrics.test_set_details).map(([key, value]) => {
                      if (key === 'metrics_included') return null;
                      return (
                        <div key={key} className="metric-item">
                          <span className="metric-label">{key.replace(/_/g, ' ')}:</span>
                          <span className="metric-value">{String(value)}</span>
                        </div>
                      );
                    })}
                  </div>
                  {modelCards.evaluation_metrics.test_set_details.metrics_included && (
                    <div className="metrics-included">
                      <span className="metrics-included-label">Metrics Included:</span>
                      <ul>
                        {modelCards.evaluation_metrics.test_set_details.metrics_included.map((metric, index) => (
                          <li key={index}>{metric}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                <div className="metrics-card">
                  <h3 className="metrics-title">Model Statistics</h3>
                  <div className="metrics-grid">
                    {Object.entries(modelCards.evaluation_metrics.model_statistics).map(([key, value]) => (
                      <div key={key} className="metric-item">
                        <span className="metric-label">{key.replace(/_/g, ' ')}:</span>
                        <span className="metric-value">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Known Limitations */}
              <div className="model-section">
                <h2 className="section-title">Known Limitations</h2>
                
                {Object.entries(modelCards.known_limitations).map(([key, limitation]) => (
                  <div key={key} className="limitation-card">
                    <h3 className="limitation-title">{key.replace(/_/g, ' ')}</h3>
                    <div className="limitation-content">
                      <div className="limitation-item">
                        <span className="limitation-label">Issue:</span>
                        <span className="limitation-value">{limitation.issue}</span>
                      </div>
                      <div className="limitation-item">
                        <span className="limitation-label">Impact:</span>
                        <span className="limitation-value">{limitation.impact}</span>
                      </div>
                      <div className="limitation-item">
                        <span className="limitation-label">Mitigation:</span>
                        <ul className="mitigation-list">
                          {limitation.mitigation.map((step, index) => (
                            <li key={index}>{step}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Mitigation Steps */}
              <div className="model-section">
                <h2 className="section-title">Mitigation Steps</h2>
                
                {Object.entries(modelCards.mitigation_steps).map(([key, steps]) => (
                  <div key={key} className="mitigation-section">
                    <h3 className="mitigation-section-title">{key.replace(/_/g, ' ')}</h3>
                    <ul className="mitigation-steps-list">
                      {steps.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TrustPage;






