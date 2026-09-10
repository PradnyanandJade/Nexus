import { useState } from 'react'
import DocumentModal from './DocumentModal'


export default function DocumentLibrary({ documents, attachedDocumentIds, hasConversation, onUpload, onDelete, onAttach, status }) {
  const [viewingDocument, setViewingDocument] = useState(null)

  return (
    <div className="library-stage">
      {/* Document Viewer Modal */}
      <DocumentModal
        isOpen={!!viewingDocument}
        document={viewingDocument}
        onClose={() => setViewingDocument(null)}
      />

      {/* Library Header */}
      <div className="library-intro">
        <div>
          <span className="eyebrow">SOURCE MATERIAL</span>
          <h2>A library with a point of view.</h2>
          <p>
            Upload the documents you want Nexus to search when a question needs
            evidence.
          </p>
        </div>
        <button className="upload" onClick={onUpload}>↑ Add document</button>
      </div>
      <div className="rule" />

      {/* Documents Grid */}
      <div className="documents">
        {documents.map((document) => (
          <article key={document.id} className="document-card">
            {/* Document Icon - Clickable to view */}
            <button
              className="file-icon-button"
              onClick={() => setViewingDocument(document)}
              title="Click to view document"
            >
              <div className="file-icon">
                {document.filename?.split('.').pop()?.toUpperCase()}
              </div>
            </button>

            {/* Document Info */}
            <div className="document-info">
              <strong>{document.filename}</strong>
              <span>Indexed source · #{document.id}</span>
            </div>

            {/* Action Buttons */}
            <div className="document-actions">
              <button
                className="attach"
                onClick={() => onAttach(document.id)}
                disabled={attachedDocumentIds.includes(document.id)}
                title={attachedDocumentIds.includes(document.id) ? 'Already attached' : 'Attach to conversation'}
              >
                {attachedDocumentIds.includes(document.id)
                  ? 'Attached'
                  : hasConversation
                    ? 'Attach'
                    : 'Use in chat'}
              </button>
              <button
                className="delete"
                onClick={() => onDelete(document.id)}
                title="Delete document"
              >
                ×
              </button>
            </div>
          </article>
        ))}

        {!documents.length && (
          <div className="empty-library">
            <b>↑</b>
            <strong>Your library is waiting.</strong>
            <p>
              PDF, DOCX, and TXT files become searchable context for your next
              conversation.
            </p>
            <button onClick={onUpload}>Upload your first source ↗</button>
          </div>
        )}
      </div>

      {/* Library Status */}
      <div className="library-status">
        <i /> {status}
      </div>
    </div>
  )
}
