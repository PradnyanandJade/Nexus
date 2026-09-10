
async def save_file_to_both_indexes(chunks,dense_index,sparse_index,embedding,bm25_encoder):
    texts = [chunk.page_content for chunk in chunks]
    dense_vectors = await embedding.aembed_documents(texts)
    dense_records = []
    for chunk, vector in zip(chunks, dense_vectors):
        dense_records.append({
            "id": chunk.metadata["chunk_id"],
            "values": vector,
            "metadata": {
                **chunk.metadata,
                "text": chunk.page_content
            }
        })
    dense_index.upsert(vectors=dense_records)

    # Sparse
    sparse_records = []
    for chunk in chunks:
        sparse_vector = bm25_encoder.encode_documents(
            [chunk.page_content]
        )[0]
        sparse_records.append({
            "id": chunk.metadata["chunk_id"],
            "sparse_values": sparse_vector,
            "metadata": {
                **chunk.metadata,
                "text": chunk.page_content
            }
        })
    sparse_index.upsert(vectors=sparse_records)
    return "File saved to both indexes successfully."

async def delete_file_from_both_indexes(user_id: int,document_id: int,dense_index,sparse_index):
    dense_index.delete(filter={"user_id": user_id,"document_id": document_id})
    sparse_index.delete(filter={"user_id": user_id,"document_id": document_id})
    return "File deleted from both indexes successfully."