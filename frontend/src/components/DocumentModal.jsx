import { useEffect, useState } from 'react'
import { getDocumentUrls } from '../services/documentService'

function normalizeDocumentUrl(value) {
  if (!value) return null

  try {
    const parsedUrl = new URL(value)
    parsedUrl.searchParams.delete('embedded')
    return parsedUrl.toString()
  } catch {
    return value
  }
}

export default function DocumentModal({ isOpen, document, onClose }) {
  const [url, setUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const supportedExtensions = ['pdf', 'docx', 'txt']

  useEffect(() => {
    if (!isOpen || !document?.id) {
      setUrl(null)
      setError(null)
      return
    }

    setLoading(true)
    setError(null)

    getDocumentUrls([document.id])
      .then((response) => {
        const documentList = Array.isArray(response?.documents)
          ? response.documents
          : []

        const matchedDocument = documentList.find(
          (item) => Number(item.document_id) === Number(document.id)
        )

        const resolvedUrl = normalizeDocumentUrl(
          matchedDocument?.url || response?.url || null
        )

        if (resolvedUrl) {
          setUrl(resolvedUrl)
        } else {
          setError('Could not load document URL')
        }
      })
      .catch((err) => {
        setError(err.message || 'Failed to load document')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [isOpen, document?.id])

  if (!isOpen) return null

  const fileExtension = document?.filename?.split('.').pop()?.toLowerCase() || ''
  const isPdf = fileExtension === 'pdf'
  const isText = fileExtension === 'txt'
  const isDocx = fileExtension === 'docx'
  const isSupported = supportedExtensions.includes(fileExtension)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content document-modal" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div>
            {/* <div className="modal-file-icon">{fileExtension.toUpperCase()}</div> */}
            {/* <h2>{document?.filename || 'Document'}</h2> */}
            {/* <p className="modal-file-info">Document #{document?.id}</p> */}
          </div>
          <button className="modal-close" onClick={onClose} title="Close">
            ×
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {loading && (
            <div className="modal-loading">
              <span>Loading document...</span>
            </div>
          )}

          {error && (
            <div className="modal-error">
              <p>{error}</p>
              {url && (
                <p>
                  <a href={url} target="_blank" rel="noopener noreferrer">
                    Download file ↗
                  </a>
                </p>
              )}
            </div>
          )}

          {!loading && !error && url && (
            <>
              {/* PDF Viewer */}
              {isPdf && (
                <iframe
                  src={url}
                  type="application/pdf"
                  className="modal-pdf-viewer"
                  title="PDF Viewer"
                />
              )}

              {/* Text Viewer */}
              {isText && (
                <div className="modal-text-viewer">
                  <iframe
                    src={url}
                    className="modal-text-iframe"
                    title="Text Viewer"
                  />
                </div>
              )}

              {/* Download for other types */}
              {!isPdf && !isText && !isDocx && (
                <div className="modal-download">
                  <p>This document type cannot be previewed.</p>
                  <a href={url} download={document.filename} className="download-button">
                    ↓ Download file
                  </a>
                </div>
              )}

              {isDocx && (
                <div className="modal-download">
                  <p>This DOCX file is supported by the backend but cannot be previewed in-browser.</p>
                  <a href={url} download={document.filename} className="download-button">
                    ↓ Download DOCX
                  </a>
                </div>
              )}
            </>
          )}    

          {!loading && !error && !url && isSupported && (
            <div className="modal-download">
              <p>Document is ready to download.</p>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        {url && (
          <div className="modal-footer">
            <a href={url} download={document.filename} className="action-button">
              ↓ Download
            </a>
            <a href={url} target="_blank" rel="noopener noreferrer" className="action-button">
              Open in new tab ↗
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
