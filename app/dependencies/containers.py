from dependency_injector import containers, providers
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings

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
    chat_model_gemma_local = providers.Singleton(
        ChatOllama,
        model="gemma2",
        base_url=str(settings.ollama_base_url),
        temperature=0.5,
    )
    embeddings_open_ai = providers.Singleton(
        AzureOpenAIEmbeddings,
        model="gpt-4o-mini",
        api_version=settings.azure_openai_api_version,
        azure_endpoint=str(settings.azure_openai_endpoint),
    )
    chat_model_open_ai = providers.Singleton(
        AzureChatOpenAI,
        model="gpt-4o-mini",
        api_version=settings.azure_openai_api_version,
        azure_endpoint=str(settings.azure_openai_endpoint),
        temperature=0.5,
    )
    vector_store = providers.Singleton(
        VectorStore,
        docs_processor=docs_processor,
        embeddings=embeddings_gemma_local,
        docs_file_path=settings.docs_path,
    )
    rag_model = providers.Factory(
        RagModel, vector_store=vector_store, llm=chat_model_gemma_local
    )
