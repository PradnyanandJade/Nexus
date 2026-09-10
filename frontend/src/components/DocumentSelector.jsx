import { useRef, useState } from 'react'
import { uploadDocument } from '../services/documentService'

export default function DocumentSelector({
  isOpen,
  documents = [],
  selectedIds = [],
  onSelect,
  onDeselect,
  onUploadSuccess,
  onClose,
}) {
  const fileInput = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  const supportedExtensions = ['.pdf', '.docx', '.txt']

  const isSupportedDocument = (file) => {
    const extension = file?.name?.split('.').pop()?.toLowerCase()
    return supportedExtensions.includes(`.${extension}`)
  }

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!isSupportedDocument(file)) {
      setUploadError('Only PDF, DOCX, and TXT files are supported by the backend.')
      if (fileInput.current) {
        fileInput.current.value = ''
      }
      return
    }

    setUploading(true)
    setUploadError(null)

    try {
      const newDocument = await uploadDocument(file)
      onUploadSuccess?.(newDocument)
      setSearchQuery('')
      // Reset file input
      if (fileInput.current) {
        fileInput.current.value = ''
      }
    } catch (error) {
      setUploadError(error.message || 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const toggleDocumentSelection = (documentId) => {
    if (selectedIds.includes(documentId)) {
      onDeselect?.(documentId)
    } else {
      onSelect?.(documentId)
    }
  }

  const filteredDocuments = documents.filter((doc) =>
    doc.filename?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content selector-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <h2>Attach Documents</h2>
            <p>Select documents to use in this conversation</p>
          </div>
          <button className="modal-close" onClick={onClose} title="Close">
            ×
          </button>
        </div>

        {/* Body */}
        <div className="modal-body selector-body">
          {/* Search Bar */}
          <div className="selector-search">
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          {/* Upload Section */}
          <div className="selector-upload">
            <div className="upload-label">
              <p>PDF, DOCX, and TXT files supported</p>
            </div>
            <label className="upload-button">
              {uploading ? 'Uploading...' : '↑ Choose file to upload'}
              <input
                ref={fileInput}
                type="file"
                onChange={handleFileSelect}
                disabled={uploading}
                accept=".pdf,.docx,.txt"
                style={{ display: 'none' }}
              />
            </label>
            {uploadError && (
              <div className="upload-error">
                <small>{uploadError}</small>
              </div>
            )}
          </div>

          <div className="selector-divider">or select from your library</div>

          {/* Documents List */}
          <div className="selector-list">
            {filteredDocuments.length > 0 ? (
              filteredDocuments.map((document) => {
                const isSelected = selectedIds.includes(document.id)
                return (
                  <div
                    key={document.id}
                    className={`selector-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => toggleDocumentSelection(document.id)}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleDocumentSelection(document.id)}
                      className="selector-checkbox"
                    />
                    <div className="selector-item-content">
                      <div className="file-icon">
                        {document.filename?.split('.').pop()?.toUpperCase() || 'FILE'}
                      </div>
                      <div>
                        <strong>{document.filename}</strong>
                        <span className="document-meta">Document #{document.id}</span>
                      </div>
                    </div>
                    <span className="selector-indicator">
                      {isSelected ? '✓' : '○'}
                    </span>
                  </div>
                )
              })
            ) : (
              <div className="selector-empty">
                {documents.length === 0 ? (
                  <>
                    <p>No documents yet.</p>
                    <p>Upload your first document above.</p>
                  </>
                ) : (
                  <p>No documents match "{searchQuery}"</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button onClick={onClose} className="action-button cancel">
            Done
          </button>
          <span className="selected-count">
            {selectedIds.length} document{selectedIds.length !== 1 ? 's' : ''} selected
          </span>
        </div>
      </div>
    </div>
  )
}
