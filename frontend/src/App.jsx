import { useEffect, useRef, useState } from 'react'
import './App.css'
import './modals.css'
import AuthPage from './components/AuthPage'
import Workspace from './components/Workspace'
import DocumentSelector from './components/DocumentSelector'
import { clearSession, getSession } from './api/client'
import { logout } from './services/authService'
import { listDocuments, uploadDocument, deleteDocument } from './services/documentService'
import { attachDocument, createConversation, deleteConversation, getAttachedDocuments, getMessages, listConversations, streamMessage } from './services/conversationService'

const ATTACHMENT_STORAGE_PREFIX = 'nexus_conversation_attachments'
const CONTEXT_STORAGE_PREFIX = 'nexus_conversation_context'
function attachmentStorageKey(userId) {
  return `${ATTACHMENT_STORAGE_PREFIX}:${userId}`
}

function loadAttachmentState(userId) {
  if (!userId) return { attachments: {}, pendingDocumentIds: [] }

  try {
    return JSON.parse(localStorage.getItem(attachmentStorageKey(userId))) || {
      attachments: {},
      pendingDocumentIds: [],
    }
  } catch {
    return { attachments: {}, pendingDocumentIds: [] }
  }
}

function contextStorageKey(userId) {
  return `${CONTEXT_STORAGE_PREFIX}:${userId}`
}

function loadContextState(userId) {
  if (!userId) return {}

  try {
    return JSON.parse(localStorage.getItem(contextStorageKey(userId))) || {}
  } catch {
    return {}
  }
}

function enrichMessages(messages, savedContexts) {
  let contextIndex = 0
  return messages.map((message) => {
    if (message.role !== 'AI') return message
    const context = savedContexts?.[contextIndex]
    contextIndex += 1
    return context ? { ...message, context } : message
  })
}

export default function App() {
  const [session, setSession] = useState(getSession)
  const [view, setView] = useState('chat')
  const [conversations, setConversations] = useState([])
  const [documents, setDocuments] = useState([])
  const [showDocumentSelector, setShowDocumentSelector] = useState(false)
  const [attachments, setAttachments] = useState(() => (
    loadAttachmentState(getSession()?.user?.id).attachments
  ))
  const [pendingDocumentIds, setPendingDocumentIds] = useState(() => (
    loadAttachmentState(getSession()?.user?.id).pendingDocumentIds
  ))
  const [conversationContexts, setConversationContexts] = useState(() => (
    loadContextState(getSession()?.user?.id)
  ))
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])
  const [composer, setComposer] = useState('')
  const [status, setStatus] = useState('Ready when you are.')
  const [error, setError] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [workspaceLoading, setWorkspaceLoading] = useState(() => Boolean(getSession()))
  const [conversationLoading, setConversationLoading] = useState(false)
  const [conversationLoadVersion, setConversationLoadVersion] = useState(0)
  const [loadedAttachmentUserId, setLoadedAttachmentUserId] = useState(
    () => getSession()?.user?.id || null
  )
  const fileInput = useRef(null)
  const conversationContextsRef = useRef(conversationContexts)
  const newlyCreatedConversationRef = useRef(null)

  useEffect(() => {
    const handleSessionExpired = () => {
      resetWorkspaceState()
      setAttachments({})
      setLoadedAttachmentUserId(null)
      setSession(null)
    }

    window.addEventListener('nexus:session-expired', handleSessionExpired)
    return () => window.removeEventListener('nexus:session-expired', handleSessionExpired)
  }, [])

  useEffect(() => {
    conversationContextsRef.current = conversationContexts
  }, [conversationContexts])

  useEffect(() => {
    const userId = session?.user?.id
    if (!userId || loadedAttachmentUserId !== userId) return

    localStorage.setItem(attachmentStorageKey(userId), JSON.stringify({
      attachments,
      pendingDocumentIds,
    }))
  }, [attachments, loadedAttachmentUserId, pendingDocumentIds, session?.user?.id])

  useEffect(() => {
    const userId = session?.user?.id
    if (!userId) return
    localStorage.setItem(contextStorageKey(userId), JSON.stringify(conversationContexts))
  }, [conversationContexts, session?.user?.id])

  useEffect(() => {
    if (!session) return

    let cancelled = false
    setWorkspaceLoading(true)
    setConversationLoading(false)
    Promise.all([listConversations(), listDocuments()]).then(async ([threads, files]) => {
      const nextThreads = Array.isArray(threads) ? threads : []
      const attachmentEntries = await Promise.all(nextThreads.map(async (thread) => {
        const threadDocuments = await getAttachedDocuments(thread.id)
        return [thread.id, (threadDocuments || []).map((document) => document.id)]
      }))
      if (cancelled) return
      setConversations(nextThreads)
      setDocuments(files || [])
      setAttachments((current) => ({
        ...current,
        ...Object.fromEntries(attachmentEntries),
      }))
      if (nextThreads.length) {
        setConversationLoading(true)
        setActiveId(nextThreads[0].id)
      } else {
        setActiveId(null)
        setMessages([])
        setConversationLoading(false)
      }
    }).catch((reason) => {
      if (!cancelled) {
        setConversationLoading(false)
        setError(reason.message)
      }
    }).finally(() => {
      if (!cancelled) setWorkspaceLoading(false)
    })

    return () => {
      cancelled = true
    }
  }, [session])

  useEffect(() => {
    if (!activeId) return undefined

    if (newlyCreatedConversationRef.current === activeId) {
      newlyCreatedConversationRef.current = null
      return undefined
    }

    let cancelled = false
    getMessages(activeId).then((nextMessages) => {
      if (cancelled) return
      setMessages(enrichMessages(nextMessages, conversationContextsRef.current[activeId]))
    }).catch((reason) => {
      if (cancelled) return
      if (reason.message.includes('404')) {
        setMessages([])
      } else {
        setError(reason.message)
      }
    }).finally(() => {
      if (!cancelled) setConversationLoading(false)
    })

    return () => {
      cancelled = true
    }
  }, [activeId, conversationLoadVersion])

  function selectConversation(conversationId) {
    setActiveId(conversationId)
    setConversationLoadVersion((version) => version + 1)
    setMessages([])
    setConversationLoading(true)
    setPendingDocumentIds([])
    setView('chat')
  }

  function startNewThread() {
    setActiveId(null)
    setMessages([])
    setComposer('')
    setConversationLoading(false)
    setPendingDocumentIds([])
    setView('chat')
  }

  function resetWorkspaceState() {
    setView('chat')
    setConversations([])
    setDocuments([])
    setActiveId(null)
    setMessages([])
    setComposer('')
    setError('')
    setStreaming(false)
    setWorkspaceLoading(false)
    setConversationLoading(false)
    setConversationLoadVersion((version) => version + 1)
    setPendingDocumentIds([])
    setConversationContexts({})
    conversationContextsRef.current = {}
    newlyCreatedConversationRef.current = null
  }

  function rememberAttachment(conversationId, documentId) {
    setAttachments((current) => ({
      ...current,
      [conversationId]: [...new Set([...(current[conversationId] || []), documentId])],
    }))
  }

  async function attachToConversation(conversationId, documentId) {
    const association = await attachDocument(conversationId, documentId)
    if (!association) {
      throw new Error('The document could not be attached to this conversation.')
    }
    rememberAttachment(conversationId, documentId)
  }

  async function handleAttachDocument(documentId) {
    setError('')
    try {
      if (!activeId) {
        setPendingDocumentIds((current) => [...new Set([...current, documentId])])
        setView('chat')
        setStatus('Source queued for your next conversation.')
        return
      }

      await attachToConversation(activeId, documentId)
      setStatus('Source attached to this conversation.')
    } catch (reason) {
      setError(reason.message)
    }
  }

  async function sendMessage(event) {
    event?.preventDefault()
    const content = composer.trim()
    if (!content || streaming) return

    setComposer('')
    setError('')
    setStreaming(true)
    setStatus('Opening a retrieval path...')
    setMessages((current) => [
      ...current,
      {
        id: `local-${Date.now()}`,
        role: 'Human',
        content,
        created_at: new Date().toISOString(),
      },
    ])

    try {
      let conversationId = activeId
      if (!conversationId) {
        const conversation = await createConversation(content.slice(0, 54) + (content.length > 54 ? '...' : ''))
        conversationId = conversation.id
        newlyCreatedConversationRef.current = conversationId
        setConversations((current) => [conversation, ...current])
        setActiveId(conversationId)

        if (pendingDocumentIds.length) {
          await Promise.all(pendingDocumentIds.map((documentId) => (
            attachToConversation(conversationId, documentId)
          )))
          setPendingDocumentIds([])
        }
      }

      let answer = ''
      let context = null
      setMessages((current) => [
        ...current,
        {
          id: `answer-${Date.now()}`,
          role: 'AI',
          content: '',
          created_at: new Date().toISOString(),
          streaming: true,
          context: null,
        },
      ])
      await streamMessage(conversationId, content, (eventData) => {
        if (eventData.type === 'status') {
          setStatus(eventData.message)
        }

        if (eventData.type === 'answer') {
          answer = eventData.content
          setMessages((current) => current.map((message) => (
            message.streaming ? { ...message, content: answer } : message
          )))
        }

        if (eventData.type === 'guardrail_block') {
          answer = eventData.message
          setMessages((current) => current.map((message) => (
            message.streaming
              ? { ...message, content: answer }
              : message
          )))
        }

        if (eventData.type === 'context') {
          context = {
            route: eventData.route,
            content: eventData.context || '',
            documents: eventData.documents || [],
          }
          setMessages((current) => current.map((message) => (
            message.streaming ? { ...message, context } : message
          )))
        }

        if (eventData.type === 'error') {
          throw new Error(eventData.message)
        }
      })
      setMessages((current) => current.map((message) => (
        message.streaming
          ? { ...message, content: answer, context, streaming: false }
          : message
      )))
      if (context) {
        setConversationContexts((current) => ({
          ...current,
          [conversationId]: [...(current[conversationId] || []), context],
        }))
      }
      setStatus('Source-aware answer complete.')
    } catch (reason) {
      setError(reason.message)
      setMessages((current) => current.filter((message) => !message.streaming))
    } finally {
      setStreaming(false)
    }
  }

  async function handleUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return

    const extension = file.name?.split('.').pop()?.toLowerCase()
    if (!['pdf', 'docx', 'txt'].includes(extension)) {
      setError('Only PDF, DOCX, and TXT files are supported by the backend.')
      event.target.value = ''
      return
    }

    try {
      setStatus(`Indexing ${file.name}...`)
      const result = await uploadDocument(file)
      setDocuments(await listDocuments())

      if (activeId) {
        await attachToConversation(activeId, result.document_id)
        setStatus('Document indexed and attached to this conversation.')
      } else {
        setPendingDocumentIds((current) => [
          ...new Set([...current, result.document_id]),
        ])
        setStatus('Document indexed and queued for your next conversation.')
      }
      
      // Keep selector open after successful upload
      setStatus('Document indexed. Continue selecting or upload more.')
    } catch (reason) {
      setError(reason.message)
    } finally {
      event.target.value = ''
    }
  }

  /**
   * Handle new document upload from the document selector modal
   */
  async function handleDocumentSelectorUpload(newDocument) {
    try {
      setDocuments(await listDocuments())
      const documentId = newDocument.document_id || newDocument.id

      if (activeId) {
        await attachToConversation(activeId, documentId)
        setStatus('Document indexed and attached to this conversation.')
      } else {
        setPendingDocumentIds((current) => [
          ...new Set([...current, documentId]),
        ])
      }
    } catch (reason) {
      setError(reason.message)
    }
  }

  /**
   * Handle document selection from the selector modal
   */
  async function handleDocumentSelect(documentId) {
    try {
      if (activeId) {
        await attachToConversation(activeId, documentId)
      } else {
        setPendingDocumentIds((current) => [...new Set([...current, documentId])])
      }
      rememberAttachment(activeId || 'pending', documentId)
      setStatus('Document attached.')
    } catch (reason) {
      setError(reason.message)
    }
  }

  /**
   * Handle document deselection from the selector modal
   */
  function handleDocumentDeselect(documentId) {
    if (activeId) {
      setAttachments((current) => ({
        ...current,
        [activeId]: (current[activeId] || []).filter((id) => id !== documentId),
      }))
    } else {
      setPendingDocumentIds((current) =>
        current.filter((id) => id !== documentId)
      )
    }
  }

  async function handleDeleteDocument(documentId) {
    try {
      await deleteDocument(documentId)
      setDocuments((current) => current.filter((document) => document.id !== documentId))
      setPendingDocumentIds((current) => current.filter((id) => id !== documentId))
      setAttachments((current) => Object.fromEntries(
        Object.entries(current).map(([conversationId, ids]) => [
          conversationId,
          ids.filter((id) => id !== documentId),
        ])
      ))
      setConversationContexts((current) => Object.fromEntries(
        Object.entries(current).map(([conversationId, contexts]) => [
          conversationId,
          contexts.map((context) => ({
            ...context,
            documents: context.documents.filter((source) => (
              source.metadata?.document_id !== documentId
            )),
          })),
        ])
      ))
    } catch (reason) {
      setError(reason.message)
    }
  }

  async function handleDeleteConversation(conversationId) {
    try {
      await deleteConversation(conversationId)
      setConversations((current) => current.filter((conversation) => conversation.id !== conversationId))
      setAttachments((current) => {
        const next = { ...current }
        delete next[conversationId]
        return next
      })
      setConversationContexts((current) => {
        const next = { ...current }
        delete next[conversationId]
        return next
      })
      if (activeId === conversationId) startNewThread()
    } catch (reason) {
      setError(reason.message)
    }
  }

  async function handleLogout() {
    await logout()
    clearSession()
    resetWorkspaceState()
    setAttachments({})
    setLoadedAttachmentUserId(null)
    setSession(null)
  }

  function handleAuthenticated(nextSession) {
    const savedState = loadAttachmentState(nextSession.user.id)
    resetWorkspaceState()
    setAttachments(savedState.attachments)
    setPendingDocumentIds(savedState.pendingDocumentIds)
    setConversationContexts(loadContextState(nextSession.user.id))
    setLoadedAttachmentUserId(nextSession.user.id)
    setWorkspaceLoading(true)
    setSession(nextSession)
  }

  if (!session) return <AuthPage onAuthenticated={handleAuthenticated} />

  const attachedDocumentIds = activeId
    ? attachments[activeId] || []
    : pendingDocumentIds
  const attachedDocuments = documents.filter((document) => (
    attachedDocumentIds.includes(document.id)
  ))

  return (
    <>
      {/* Document Selection Modal */}
      <DocumentSelector
        isOpen={showDocumentSelector}
        documents={documents}
        selectedIds={attachedDocumentIds}
        onSelect={handleDocumentSelect}
        onDeselect={handleDocumentDeselect}
        onUploadSuccess={handleDocumentSelectorUpload}
        onClose={() => setShowDocumentSelector(false)}
      />

      {/* Main Workspace */}
      <Workspace
        session={session}
        view={view}
        conversations={conversations}
        documents={documents}
        attachedDocuments={attachedDocuments}
        attachedDocumentIds={attachedDocumentIds}
        activeId={activeId}
        messages={messages}
        composer={composer}
        status={status}
        error={error}
        streaming={streaming}
        workspaceLoading={workspaceLoading}
        conversationLoading={conversationLoading}
        setComposer={setComposer}
        onViewChange={setView}
        onSelectConversation={selectConversation}
        onNewThread={startNewThread}
        onDeleteConversation={handleDeleteConversation}
        onLogout={handleLogout}
        onSend={sendMessage}
        onUpload={() => setShowDocumentSelector(true)}
        onDeleteDocument={handleDeleteDocument}
        onAttachDocument={handleAttachDocument}
        clearError={() => setError('')}
      />
      {/* Hidden file input - kept for backward compatibility */}
      <input
        ref={fileInput}
        className="hidden"
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleUpload}
      />
    </>
  )
}
