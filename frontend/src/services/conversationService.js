import { apiRequest, streamRequest } from '../api/client'

export const listConversations = () => apiRequest('/conversations/')
export const getConversation = (conversationId) => apiRequest(`/conversations/${conversationId}`)
export const createConversation = (title) => apiRequest('/conversations/', { method: 'POST', body: JSON.stringify({ title }) })
export const updateConversation = (conversationId, title) => apiRequest(`/conversations/${conversationId}`, { method: 'PUT', body: JSON.stringify({ title }) })
export const deleteConversation = (conversationId) => apiRequest(`/conversations/${conversationId}`, { method: 'DELETE' })
export const getMessages = (conversationId) => apiRequest(`/conversations/${conversationId}/messages`)
export const getAttachedDocuments = (conversationId) => apiRequest(`/conversations/${conversationId}/documents`)
export const sendMessage = (conversationId, content) => apiRequest(`/conversations/${conversationId}/chat`, { method: 'POST', body: JSON.stringify({ content }) })
export const attachDocument = (conversationId, documentId) => apiRequest(`/conversations/${conversationId}/documents/${documentId}`, { method: 'POST' })
export const streamMessage = (conversationId, content, onEvent) => streamRequest(`/conversations/${conversationId}/stream-chat`, { content }, onEvent)
