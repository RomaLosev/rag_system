import json
import shutil
from pathlib import Path

from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_core.documents import Document
from loguru import logger

from app.common.exceptions import UnsupportedFileError
from app.core.config import settings
from app.utils.docs_splitter import split_docx_by_size_generator, split_xlsx


class MicrosoftDocumentsLoader:
    @staticmethod
    def save_documents(docs: list[Document], file_path: str):
        """
        Save documents to JSON file.
        """
        data = [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Documents saved in {file_path}")

    @staticmethod
    def load_documents_from_json_file(file_path: str) -> list[Document]:
        """
        Load documents from JSON.
        """
        if not Path(file_path).exists():
            msg = f"File {file_path} not found."
            raise FileNotFoundError(msg)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [
            Document(page_content=item["content"], metadata=item["metadata"])
            for item in data
        ]

    @staticmethod
    def load_documents(file_path: Path):
        """Just change loader if needed."""
        loader = AzureAIDocumentIntelligenceLoader(
            api_endpoint=settings.azure_docs_loader_endpoint,
            api_key=settings.azure_docs_loader_key,
            file_path=str(file_path),
        )
        return loader.load()

    @staticmethod
    def delete_folder(folder_path: Path):
        if folder_path.exists() and folder_path.is_dir():
            shutil.rmtree(folder_path)

    def load_document_docx(self, file_path: Path) -> list[Document]:
        document = []
        output_path = Path("./temp_files_dir")
        for file_part in split_docx_by_size_generator(
            file_path, output_path, max_size_mb=3
        ):
            try:
                doc_part = self.load_documents(file_part)
                document.extend(doc_part)
            except Exception as ex:
                logger.error(f"Can not load document {file_path}: {ex}")
        self.delete_folder(output_path)
        return document

    def load_document_xlsx(self, file_path: Path) -> list[Document]:
        documents = []
        output_path = Path("./temp_files_dir")
        for file_part in split_xlsx(file_path, output_path):
            try:
                doc_part = self.load_documents(file_part)
                documents.extend(doc_part)
            except Exception as ex:
                logger.error(f"Error with excel part {file_part}: {ex}")
            finally:
                file_part.unlink(missing_ok=True)
        return documents

    @staticmethod
    def check_documents(folder_path: Path) -> bool:
        """Check unsupported documents in docs folder."""
        supported_files = (".xlsx", ".docx")
        unsupported_files = [
            doc.name
            for doc in folder_path.iterdir()
            if doc.is_file() and doc.suffix not in supported_files
        ]
        if unsupported_files:
            raise UnsupportedFileError(
                details={
                    "files": unsupported_files,
                    "supported_extensions": supported_files,
                }
            )
        return True

    def load_microsoft_documents(self, folder_path: Path) -> list[Document]:
        documents = []
        self.check_documents(folder_path)
        for file_path in folder_path.iterdir():
            match file_path.suffix:
                case ".docx":
                    parsed_doc = self.load_document_docx(file_path)
                case ".xlsx":
                    parsed_doc = self.load_document_xlsx(file_path)
                case _:
                    logger.warning(f"Unknown file format: {file_path}")
                    continue
            documents.extend(parsed_doc)
        return documents
