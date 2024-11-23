from dependency_injector import containers, providers
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from app.ai_model.rag_model import RagModel
from app.ai_model.vectorstore import VectorStore
from app.core.config import settings
from app.utils.docs_loader import MicrosoftDocumentsLoader


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api"])

    docs_processor = providers.Resource(MicrosoftDocumentsLoader)
    embeddings_gemma_local = providers.Singleton(
        OllamaEmbeddings, model="gemma2", base_url=str(settings.ollama_base_url)
    )
    chat_model_gemma = providers.Singleton(
        ChatOpenAI,
        model="google/gemma-2-9b-it",
        base_url=str(settings.gemma_base_url),
        api_key=settings.gemma_api_key,
        stream_usage=True,
        temperature=0.8,
    )
    embeddings_openai = providers.Singleton(
        OpenAIEmbeddings,
        api_key=settings.openai_api_key,
    )
    chat_model_gemma_local = providers.Singleton(
        ChatOllama,
        model="gemma2",
        base_url=str(settings.ollama_base_url),
        temperature=0.2,
    )
    vector_store = providers.Singleton(
        VectorStore,
        docs_processor=docs_processor,
        embeddings=embeddings_openai,
        docs_file_path=settings.docs_path,
    )
    rag_model = providers.Factory(
        RagModel, vector_store=vector_store, llm=chat_model_gemma
    )
