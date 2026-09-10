import ChatPanel from './ChatPanel'
import DocumentLibrary from './DocumentLibrary'
import Sidebar from './Sidebar'

export default function Workspace({ session, view, conversations, documents, attachedDocuments, attachedDocumentIds, activeId, messages, composer, status, error, streaming, workspaceLoading, conversationLoading, setComposer, onViewChange, onSelectConversation, onNewThread, onDeleteConversation, onLogout, onSend, onUpload, onDeleteDocument, onAttachDocument, clearError }) {
  const active = conversations.find((conversation) => conversation.id === activeId)
  return (
    <main className="app-shell">
      <Sidebar
        user={session.user}
        view={view}
        conversations={conversations}
        documentCount={documents.length}
        activeId={activeId}
        onViewChange={onViewChange}
        onSelectConversation={onSelectConversation}
        onNewThread={onNewThread}
        onDeleteConversation={onDeleteConversation}
        onLogout={onLogout}
      />
      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">
              {view === 'chat' ? 'RESEARCH DESK' : 'KNOWLEDGE BASE'}
            </span>
            <h1>
              {view === 'chat' ? (active?.title || 'Untitled research') : 'Your source library'}
            </h1>
          </div>
          <span className="online">
            <i /> System online <b /> {session.user.username}
          </span>
        </header>
        {error && (
          <div className="error-banner">
            {error}
            <button onClick={clearError}>×</button>
          </div>
        )}
        {view === 'library' ? (
          <DocumentLibrary
            documents={documents}
            attachedDocumentIds={attachedDocumentIds}
            hasConversation={Boolean(activeId)}
            onUpload={onUpload}
            onDelete={onDeleteDocument}
            onAttach={onAttachDocument}
            status={status}
          />
        ) : (
          <ChatPanel
            messages={messages}
            text={composer}
            setText={setComposer}
            onSend={onSend}
            onUpload={onUpload}
            streaming={streaming}
            status={status}
            attachedDocuments={attachedDocuments}
            hasDocuments={attachedDocuments.length > 0}
            documents={documents}
            isLoading={workspaceLoading || conversationLoading}
            loadingLabel={workspaceLoading ? 'Preparing your workspace...' : 'Loading conversation...'}
          />
        )}
      </section>
    </main>
  )
}
