from langchain_core.documents import Document

class HybridRetriever:
    def __init__(self,dense_index,sparse_index,embedding,sparse_encoder,reranker):
        self.dense_index = dense_index
        self.sparse_index = sparse_index
        self.embedding = embedding
        self.sparse_encoder = sparse_encoder
        self.reranker = reranker

    async def retrieve(self,query:str,document_ids: list[int]):
        dense_vector = await self.embedding.aembed_query(query)
        dense_result = self.dense_index.query(
            vector = dense_vector,
            top_k = 10,
            include_metadata = True,
            filter={
                "document_id": {
                    "$in": document_ids
                }
            }
        )
        sparse_vector = self.sparse_encoder.encode_queries(query)
        sparse_result = self.sparse_index.query(
            sparse_vector = sparse_vector,
            top_k = 10,
            include_metadata = True,
            filter={
                "document_id": {
                    "$in": document_ids
                }
            }
        )
        return dense_result, sparse_result

    def reciprocal_rank_fusion(self,dense_result,sparse_result,k:int=60):
        scores = {}
        documents = {}
        results = [
            dense_result.matches,
            sparse_result.matches
        ]
        for result_list in results:
            for rank,match in enumerate(result_list,start=1):
                doc_id = match.id
                scores[doc_id] = (scores.get(doc_id,0)+(1/(k+rank)))
                documents[doc_id] = Document(
                    page_content=match.metadata.get("text",""),
                    metadata={
                        **match.metadata,
                        "chunk_id":match.id,
                        "score":match.score
                    }
                )

        ranked_ids = sorted(scores,key=scores.get,reverse=True)
        return [documents[doc_id] for doc_id in ranked_ids]


    def rerank(self,query,documents,top_k:int=5):
        candidates_text = [
            document.page_content
            for document in documents
        ]
        response = self.reranker.rerank(
            model = "rerank-v4.0-fast",
            query=query,
            documents=candidates_text,
            top_n = top_k
        )
        return [
            documents[result.index]
            for result in response.results
        ]