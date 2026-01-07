/**
 * Loading Skeleton Components
 * Reusable skeleton loaders for different content types
 */
import './LoadingSkeleton.css';

interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
}

/**
 * Base skeleton element
 */
export const Skeleton = ({ 
  className = '', 
  width, 
  height, 
  borderRadius = '0.25rem' 
}: SkeletonProps) => {
  const style: React.CSSProperties = {
    width: width || '100%',
    height: height || '1rem',
    borderRadius,
  };

  return (
    <div className={`skeleton ${className}`} style={style} />
  );
};

/**
 * Skeleton for career cards
 */
export const CareerCardSkeleton = () => {
  return (
    <div className="career-card-skeleton">
      <div className="skeleton-header">
        <Skeleton width="60%" height="1.5rem" />
        <Skeleton width="4rem" height="1.5rem" borderRadius="1rem" />
      </div>
      <Skeleton width="100%" height="1rem" className="skeleton-margin" />
      <Skeleton width="80%" height="1rem" className="skeleton-margin" />
      <Skeleton width="100%" height="3rem" className="skeleton-margin" />
      <div className="skeleton-footer">
        <Skeleton width="30%" height="0.875rem" />
        <Skeleton width="40%" height="0.875rem" />
      </div>
    </div>
  );
};

/**
 * Skeleton for form sections
 */
export const FormSectionSkeleton = () => {
  return (
    <div className="form-section-skeleton">
      <Skeleton width="40%" height="1.25rem" className="skeleton-margin" />
      <Skeleton width="100%" height="2.5rem" className="skeleton-margin" />
      <Skeleton width="100%" height="2.5rem" className="skeleton-margin" />
      <Skeleton width="60%" height="2.5rem" />
    </div>
  );
};

/**
 * Skeleton for list items
 */
export const ListItemSkeleton = ({ count = 3 }: { count?: number }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="list-item-skeleton">
          <Skeleton width="100%" height="1.25rem" />
          <Skeleton width="70%" height="0.875rem" className="skeleton-margin" />
        </div>
      ))}
    </>
  );
};

/**
 * Skeleton for table rows
 */
export const TableRowSkeleton = ({ columns = 4 }: { columns?: number }) => {
  return (
    <tr className="table-row-skeleton">
      {Array.from({ length: columns }).map((_, index) => (
        <td key={index}>
          <Skeleton width="80%" height="1rem" />
        </td>
      ))}
    </tr>
  );
};

/**
 * Skeleton for page content
 */
export const PageSkeleton = () => {
  return (
    <div className="page-skeleton">
      <Skeleton width="40%" height="2rem" className="skeleton-margin" />
      <Skeleton width="100%" height="1.5rem" className="skeleton-margin" />
      <div className="skeleton-grid">
        <CareerCardSkeleton />
        <CareerCardSkeleton />
        <CareerCardSkeleton />
      </div>
    </div>
  );
};

export default Skeleton;




