from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore as VectorStoreBase
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from app.core.config import settings
from app.utils.docs_loader import MicrosoftDocumentsLoader


class VectorStore:
    def __init__(
        self,
        docs_processor: MicrosoftDocumentsLoader,
        embeddings: Embeddings,
        docs_file_path: Path,
    ):
        self.docs_processor = docs_processor
        self.embeddings = embeddings
        self.vector_store: VectorStoreBase = self.create_vectorstore(docs_file_path)

    def create_vectorstore(self, docs_file_path: Path) -> VectorStoreBase:
        saved_docs_file_path = Path(settings.docs_path / "saved_docs.json")
        if saved_docs_file_path.exists():
            logger.info("Loading saved documents...")
            docs = self.docs_processor.load_documents_from_json_file(
                str(saved_docs_file_path)
            )
            rewrite = False
        else:
            logger.info("Saved documents not found, parsing...")
            docs = self.docs_processor.load_microsoft_documents(docs_file_path)
            self.docs_processor.save_documents(docs, str(saved_docs_file_path))
            rewrite = True
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        splits = text_splitter.split_documents(docs)
        return self.create_or_load_faiss_index(self.embeddings, splits, rewrite)

    @staticmethod
    def create_or_load_faiss_index(
        embeddings_model: Embeddings, documents: list[Document], rewrite: bool
    ) -> FAISS:
        faiss_index_path = Path(settings.docs_path / "faiss_index")
        if not faiss_index_path.exists() or rewrite:
            vectorstore = FAISS.from_documents(documents, embeddings_model)
            vectorstore.save_local(str(faiss_index_path))
            logger.info("FAISS index created and saved.")
        else:
            vectorstore = FAISS.load_local(
                str(faiss_index_path),
                embeddings_model,
                allow_dangerous_deserialization=True,
            )
            logger.info("FAISS index loaded from local file.")
        return vectorstore

    async def create_embeddings(self, message: str) -> list[float]:
        return await self.embeddings.aembed_query(message)

    async def vector_search(self, message: str) -> list[Document]:
        embedding = await self.create_embeddings(message)
        return await self.vector_store.amax_marginal_relevance_search_by_vector(
            embedding=embedding, k=10
        )
