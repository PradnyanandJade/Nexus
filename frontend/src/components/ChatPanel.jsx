import { useState } from 'react'
import MarkdownMessage from "./MarkDownMessage"
import DocumentModal from './DocumentModal'

const dateLabel = (value) =>
  value
    ? new Intl.DateTimeFormat('en', {
        month: 'short',
        day: 'numeric',
      }).format(new Date(value))
    : ''


function ContextDetails({ context, onDocumentClick }) {
  if (!context) return null

  const isWeb = context.route === 'web'

  return (
    <details className="message-context">
      <summary>
        {isWeb ? 'WEB SOURCES' : 'RETRIEVED DOCUMENT CONTEXT'}
        <span>{context.documents?.length || 0} sources</span>
      </summary>

      <div className="context-sources">
        {context.documents?.map((source, index) => {
          const metadata = source.metadata || {}
          const label =
            metadata.title ||
            metadata.file_name ||
            (metadata.document_id
              ? `Document #${metadata.document_id}`
              : `Source ${index + 1}`)
          return (
            <details
              className="context-source"
              key={`${label}-${index}`}
            >

              {/* ONLY THIS toggles the chunk */}
              <summary>
                <span className="context-document-name">
                  📄 {label}
                </span>

                {metadata.score !== undefined && (
                  <bold className="context-document-name">
                    Score {Number(metadata.score).toFixed(2)}
                  </bold>
                )}
                {metadata.page !== undefined && (
                  <bold className="context-document-name">
                    - Page:{Number(metadata.page)}
                  </bold>
                )}
              </summary>

              <div className="context-content-wrapper">

                {metadata.url && (
                  <div className="context-file-actions">
                    <a
                      href={metadata.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="context-file-link"
                      title="Open in new tab"
                    >
                      Open in new tab ↗
                    </a>
                  </div>
                )}

                {metadata.text && (
                  <pre className="context-content">
                    {metadata.text}
                  </pre>
                )}

              </div>

            </details>
          )
        })}
      </div>
    </details>
  )
}

export default function ChatPanel({
  messages,
  text,
  setText,
  onSend,
  onUpload,
  streaming,
  status,
  attachedDocuments,
  hasDocuments,
  documents = [],
  isLoading = false,
  loadingLabel = 'Loading conversation...',
}) {
  const [viewingDocument, setViewingDocument] = useState(null)

  // Find document by ID for viewing
  const handleDocumentClick = (documentId, label) => {
    const document = documents.find((doc) => doc.id === documentId)
    if (document) {
      setViewingDocument(document)
    }
  }
  return (
    <div className="chat-stage">
      {/* Document Viewer Modal */}
      <DocumentModal
        isOpen={!!viewingDocument}
        document={viewingDocument}
        onClose={() => setViewingDocument(null)}
      />

      <div className="chat-content">
        {isLoading ? (
          <div className="chat-loading" role="status" aria-live="polite">
            <div className="loading-mark" aria-hidden="true">
              <i /><i /><i />
            </div>
            <span>{loadingLabel}</span>
            <small>Gathering your research space</small>
          </div>
        ) : !messages.length ? (
          <div className="welcome">
            <div className="number">01</div>

            <span className="eyebrow">NEXUS / READY</span>

            <h2>
              Bring a question.
              <br />
              <i>Leave with a map.</i>
            </h2>

            <p>
              Search across your own documents, reach for the web, or simply
              think out loud. Nexus keeps the trail visible.
            </p>

            <div className="suggestions">
              <button
                onClick={() =>
                  setText('What are the key themes in my research?')
                }
              >
                ↗ Find a pattern in my sources
              </button>

              <button
                onClick={() =>
                  setText(
                    'Compare the strongest arguments I have collected.'
                  )
                }
              >
                ↗ Compare two ideas
              </button>
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((message) => (
              <article
                className={`message ${
                  message.role === 'Human' ? 'human' : 'assistant'
                }`}
                key={message.id}
              >
                <div className="message-meta">
                  <span>
                    {message.role === 'Human' ? 'YOU' : 'NEXUS'}
                  </span>

                  <time>{dateLabel(message.created_at)}</time>
                </div>

                <div className="message-body">
                  {message.content ? (
                    message.role === 'Human' ? (
                      // User messages remain normal text
                      message.content
                    ) : (
                      // AI messages are rendered as Markdown
                        <MarkdownMessage content={message.content} />
                    )
                  ) : (
                    <span className="typing">
                      <i />
                      <i />
                      <i />
                    </span>
                  )}
                </div>
                {message.role !== 'Human' && (
                  <ContextDetails
                    context={message.context}
                    onDocumentClick={handleDocumentClick}
                  />
                )}
              </article>
            ))}
          </div>
        )}
      </div>

      {!isLoading && <div className="composer-wrap">
        <div className="status-line">
          <i /> {status}
          <span>
            {hasDocuments ? 'DOCS CONNECTED' : 'NO DOCS YET'}
          </span>
        </div>
        <div className="attached-sources">
          <span> SOURCES</span>
          {attachedDocuments.length ? (
            attachedDocuments.map((document) => (
              <span className="source-chip" key={document.id}>
                {document.filename}
              </span>
            ))
          ) : (
            <span className="source-empty">Attach a document from the knowledge base.</span>
          )}
        </div>

        <form className="composer" onSubmit={onSend}>
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                onSend(event)
              }
            }}
            placeholder="Ask something worth following..."
            rows="2"
          />

          <div>
            <button type="button" onClick={onUpload}>
              + Add source
            </button>

            <small>Shift + Enter for a new line</small>

            <button
              className="send"
              disabled={streaming || !text.trim()}
            >
              ↗
            </button>
          </div>
        </form>
      </div>}
    </div>
  )
}