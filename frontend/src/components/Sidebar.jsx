const dateLabel = (value) => value ? new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(new Date(value)) : ''

export default function Sidebar({ user, view, conversations, documentCount, activeId, onViewChange, onSelectConversation, onNewThread, onDeleteConversation, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <b>N</b>
        <span>
          NEXUS 
        </span>
      </div>
      <button className="new-thread" onClick={onNewThread}>
        <span>+</span> New thread <kbd>CMD K</kbd>
      </button>
      <nav>
        <button
          className={view === 'chat' ? 'active' : ''}
          onClick={() => onViewChange('chat')}
        >
          <span>◌</span> Ask Nexus
        </button>
        <button
          className={view === 'library' ? 'active' : ''}
          onClick={() => onViewChange('library')}
        >
          <span>▤</span> Knowledge base <em>{documentCount}</em>
        </button>
      </nav>
      <div className="history-label">
        <span>RECENT THREADS</span>
        <span>{conversations.length}</span>
      </div>
      <div className="thread-list">
        {conversations.map((conversation) => (
          <div
            className={`thread ${activeId === conversation.id && view === 'chat' ? 'selected' : ''}`}
            key={conversation.id}
          >
            <button onClick={() => onSelectConversation(conversation.id)}>
              <strong>{conversation.title}</strong>
              <small>{dateLabel(conversation.created_at)}</small>
            </button>
            <button
              className="delete"
              onClick={() => onDeleteConversation(conversation.id)}
              title="Delete thread"
            >
              X
            </button>
          </div>
        ))}
        {!conversations.length && (
          <p className="empty-sidebar">Your threads will appear here.</p>
        )}
      </div>
      <div className="sidebar-footer">
        <div className="avatar">{user.username[0].toUpperCase()}</div>
        <div>
          <strong>{user.username}</strong>
          <small>Personal workspace</small>
        </div>
        <button onClick={onLogout} title="Sign out">↗</button>
      </div>
    </aside>
  )
}
