from pathlib import Path
from langchain_community.document_loaders import (PyPDFLoader,Docx2txtLoader,TextLoader,)
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_loader(file_path:str):
    """Get the appropriate loader based on the file extension."""
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(file_path)
    elif suffix == ".docx":
        return Docx2txtLoader(file_path)
    elif suffix == ".txt":
        return TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF, DOCX, and TXT files are allowed.")

        
async def chunk_file(file_name:str,file_path:str,chunk_size:int,chunk_overlap:int,user_id:str,document_id:int):
    """Chunk the file into smaller pieces."""
    loader = get_loader(file_path)    
    documents = await loader.aload()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)
    for index,chunk in enumerate(chunks):
        chunk.metadata["user_id"] = user_id
        chunk.metadata["document_id"] = document_id
        chunk.metadata["chunk_id"] = f"{document_id}_{index}"
        chunk.metadata["file_name"] = file_name

    return chunks

