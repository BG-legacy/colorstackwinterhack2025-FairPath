import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './CatalogDetailPage.css';
import dataService, { OccupationCatalog } from '../services/data';

interface Particle {
  x: number;
  y: number;
  size: number;
  opacity: number;
  speed: number;
}

/**
 * CatalogDetailPage Component
 * Displays detailed information about a specific occupation
 * Route: /catalog/:careerId
 */
function CatalogDetailPage(): JSX.Element {
  const { careerId } = useParams<{ careerId: string }>();
  const navigate = useNavigate();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [occupation, setOccupation] = useState<OccupationCatalog | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Load occupation details
  useEffect(() => {
    const loadOccupation = async (): Promise<void> => {
      if (!careerId) {
        setError('Career ID is required');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError('');

      try {
        const data = await dataService.getOccupationById(careerId);
        setOccupation(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load occupation details');
        setOccupation(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadOccupation();
  }, [careerId]);

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

      particles.forEach((particle) => {
        particle.y += particle.speed;
        if (particle.y > canvas.height) {
          particle.y = 0;
          particle.x = Math.random() * canvas.width;
        }

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity * 0.1})`;
        ctx.fill();
      });

      requestAnimationFrame(animate);
    };

    animate();

    return (): void => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  if (isLoading) {
    return (
      <div className="catalog-detail-page">
        <canvas ref={canvasRef} className="particles-canvas" />
        <div className="catalog-detail-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading occupation details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !occupation) {
    return (
      <div className="catalog-detail-page">
        <canvas ref={canvasRef} className="particles-canvas" />
        <div className="catalog-detail-container">
          <button className="back-button" onClick={() => navigate('/catalog')}>
            ← Back to Catalog
          </button>
          <div className="error-banner">
            {error || 'Occupation not found'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="catalog-detail-page">
      <canvas ref={canvasRef} className="particles-canvas" />
      <div className="catalog-detail-container">
        <button className="back-button" onClick={() => navigate('/catalog')}>
          ← Back to Catalog
        </button>

        <div className="detail-content">
          <div className="detail-header">
            <h1 className="detail-title">{occupation.occupation.name}</h1>
            {occupation.occupation.soc_code && (
              <span className="detail-soc">{occupation.occupation.soc_code}</span>
            )}
          </div>

          {/* Description */}
          <div className="detail-section">
            <h2 className="detail-section-title">Description</h2>
            <p className="detail-text">{occupation.occupation.description}</p>
          </div>

          {/* BLS Projections */}
          {occupation.bls_projection && (
            <div className="detail-section">
              <h2 className="detail-section-title">BLS Employment Projections</h2>
              <div className="bls-grid">
                {occupation.bls_projection.employment_2024 && (
                  <div className="bls-item">
                    <span className="bls-label">Employment 2024:</span>
                    <span className="bls-value">
                      {occupation.bls_projection.employment_2024.toLocaleString()} (thousands)
                    </span>
                  </div>
                )}
                {occupation.bls_projection.employment_2034 && (
                  <div className="bls-item">
                    <span className="bls-label">Projected Employment 2034:</span>
                    <span className="bls-value">
                      {occupation.bls_projection.employment_2034.toLocaleString()} (thousands)
                    </span>
                  </div>
                )}
                {occupation.bls_projection.percent_change !== undefined && (
                  <div className="bls-item">
                    <span className="bls-label">Percent Change:</span>
                    <span className="bls-value">
                      {occupation.bls_projection.percent_change > 0 ? '+' : ''}
                      {occupation.bls_projection.percent_change.toFixed(1)}%
                    </span>
                  </div>
                )}
                {occupation.bls_projection.median_wage_2024 && (
                  <div className="bls-item">
                    <span className="bls-label">Median Wage 2024:</span>
                    <span className="bls-value">
                      ${occupation.bls_projection.median_wage_2024.toLocaleString()}/year
                    </span>
                  </div>
                )}
                {occupation.bls_projection.annual_openings && (
                  <div className="bls-item">
                    <span className="bls-label">Annual Openings:</span>
                    <span className="bls-value">
                      {occupation.bls_projection.annual_openings.toLocaleString()}
                    </span>
                  </div>
                )}
                {occupation.bls_projection.typical_education && (
                  <div className="bls-item">
                    <span className="bls-label">Typical Education:</span>
                    <span className="bls-value">
                      {occupation.bls_projection.typical_education}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Skills */}
          {occupation.skills.length > 0 && (
            <div className="detail-section">
              <h2 className="detail-section-title">Skills ({occupation.skills.length})</h2>
              <div className="skills-list-detail">
                {occupation.skills
                  .sort((a, b) => (b.importance || 0) - (a.importance || 0))
                  .map((skill, index) => (
                    <div key={index} className="skill-item-detail">
                      <span className="skill-name-detail">{skill.skill_name}</span>
                      {skill.importance !== undefined && (
                        <span className="skill-importance">
                          Importance: {skill.importance.toFixed(1)}
                        </span>
                      )}
                      {skill.level !== undefined && (
                        <span className="skill-level">Level: {skill.level.toFixed(1)}</span>
                      )}
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Tasks */}
          {occupation.tasks.length > 0 && (
            <div className="detail-section">
              <h2 className="detail-section-title">Tasks ({occupation.tasks.length})</h2>
              <ul className="tasks-list-detail">
                {occupation.tasks.map((task, index) => (
                  <li key={index} className="task-item-detail">
                    {task.task_description}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CatalogDetailPage;






