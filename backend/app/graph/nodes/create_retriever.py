from app.graph.state import GraphState

def create_retriever(retriever):
    async def context_retriever(state: GraphState):
        query = state["rewritten_query"]
        document_ids = state["document_ids"]
        if not document_ids:
            return {
                "context_documents": [],
                "context": ""
            }
        dense_result,sparse_result = await retriever.retrieve(query=query,document_ids=document_ids)
        hybrid_retrieval_documents = retriever.reciprocal_rank_fusion(dense_result,sparse_result,k=60)
        reranked_documents = retriever.rerank(query,hybrid_retrieval_documents,top_k=5)
        context = "\n".join(document.page_content for document in reranked_documents)
        return {
            "context_documents":reranked_documents,
            "context":context
        }
    return context_retriever