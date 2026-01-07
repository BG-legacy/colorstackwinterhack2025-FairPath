/**
 * FilePreview Component
 * Component for previewing uploaded files (PDF and text files)
 */
import { useEffect, useState } from 'react';
import {
  getFileMetadata,
  isPdfFile,
  isTextFile,
  readTextFile,
  createFilePreviewUrl,
  FileMetadata,
} from '../utils/fileUpload';
import './FilePreview.css';

interface FilePreviewProps {
  file: File;
  onClose?: () => void;
  className?: string;
}

export function FilePreview({ file, onClose, className = '' }: FilePreviewProps): JSX.Element {
  const [metadata, setMetadata] = useState<FileMetadata | null>(null);
  const [textContent, setTextContent] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Get file metadata
    const fileMetadata = getFileMetadata(file);
    setMetadata(fileMetadata);

    // Create preview URL for PDF
    if (isPdfFile(file)) {
      const url = createFilePreviewUrl(file);
      setPreviewUrl(url);
      setIsLoading(false);
      return () => {
        URL.revokeObjectURL(url);
      };
    }

    // Read text file content
    if (isTextFile(file)) {
      readTextFile(file)
        .then((content) => {
          setTextContent(content);
          setIsLoading(false);
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : 'Failed to read file');
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, [file]);

  // Cleanup preview URL on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  if (isLoading) {
    return (
      <div className={`file-preview-container ${className}`}>
        <div className="file-preview-loading">Loading preview...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`file-preview-container ${className}`}>
        <div className="file-preview-error">{error}</div>
      </div>
    );
  }

  return (
    <div className={`file-preview-container ${className}`}>
      {/* File Metadata */}
      {metadata && (
        <div className="file-preview-metadata">
          <div className="file-metadata-row">
            <span className="file-metadata-label">Name:</span>
            <span className="file-metadata-value">{metadata.name}</span>
          </div>
          <div className="file-metadata-row">
            <span className="file-metadata-label">Size:</span>
            <span className="file-metadata-value">{metadata.formattedSize}</span>
          </div>
          <div className="file-metadata-row">
            <span className="file-metadata-label">Type:</span>
            <span className="file-metadata-value">{metadata.type || metadata.extension.toUpperCase()}</span>
          </div>
          <div className="file-metadata-row">
            <span className="file-metadata-label">Modified:</span>
            <span className="file-metadata-value">
              {new Date(metadata.lastModified).toLocaleString()}
            </span>
          </div>
        </div>
      )}

      {/* Close button */}
      {onClose && (
        <button
          type="button"
          className="file-preview-close"
          onClick={onClose}
          aria-label="Close preview"
        >
          ×
        </button>
      )}

      {/* PDF Preview */}
      {isPdfFile(file) && previewUrl && (
        <div className="file-preview-content">
          <iframe
            src={previewUrl}
            className="file-preview-iframe"
            title="PDF Preview"
            sandbox="allow-same-origin allow-scripts"
          />
        </div>
      )}

      {/* Text Preview */}
      {isTextFile(file) && textContent !== null && (
        <div className="file-preview-content">
          <pre className="file-preview-text">{textContent}</pre>
        </div>
      )}

      {/* Unsupported file type */}
      {!isPdfFile(file) && !isTextFile(file) && (
        <div className="file-preview-unsupported">
          <p>Preview not available for this file type.</p>
          <p>File type: {metadata?.type || metadata?.extension || 'unknown'}</p>
        </div>
      )}
    </div>
  );
}

export default FilePreview;






