from src.processing.chunker import chunk_documents
from src.ingestion import load_corpus
from src.processing.embedder import Embedder
from src.vectorstore import VectorStore

class IngestionPipeline:
    def __init__(self, embedder: Embedder, store: VectorStore):
        self.embedder = embedder
        self.store = store

    def build_index(self) -> dict:
        docs = load_corpus()
        chunks = chunk_documents(docs)
        if chunks:
            ids = [c.chunk_id for c in chunks]
            texts = [c.text for c in chunks]
            metas = [c.metadata for c in chunks]
            self.store.add(ids=ids, texts=texts, metadatas=metas)
        return {
            "documents": len(docs),
            "chunks": len(chunks),
            "vectorstore_backend": self.store.backend,
            "embedding_backend": self.embedder.backend,
        }
