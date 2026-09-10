import { apiRequest } from '../api/client'

/**
 * Fetch all documents for the current user
 * @returns {Promise<Array>} List of document objects with metadata
 */
export const listDocuments = () => apiRequest('/documents/')

/**
 * Get a specific document by ID
 * @param {number} documentId - The document ID
 * @returns {Promise<Object>} Document object
 */
export const getDocument = (documentId) => apiRequest(`/documents/${documentId}`)

/**
 * Upload a new document to the server
 * @param {File} file - The file to upload
 * @returns {Promise<Object>} Created document object
 */
export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiRequest('/documents/upload', { method: 'POST', body: formData })
}

/**
 * Delete a document permanently
 * @param {number} documentId - The document ID to delete
 * @returns {Promise<Object>} Success response
 */
export const deleteDocument = (documentId) => apiRequest(`/documents/delete/${documentId}`, { method: 'DELETE' })

/**
 * Get S3 URLs for multiple documents to view/download
 * @param {Array<number>} documentIds - Array of document IDs
 * @returns {Promise<Object>} Object with URLs for each document
 */
export const getDocumentUrls = (documentIds) => 
  apiRequest('/documents/urls', {
    method: 'POST',
    body: JSON.stringify({ document_ids: documentIds }),
  })
