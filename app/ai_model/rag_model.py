import json

from langchain_core.language_models import BaseChatModel
from loguru import logger

from app.ai_model.vectorstore import VectorStore
from app.common.prompts import (
    answer_prompt,
    check_question_prompt,
    re_write_prompt,
    simple_question,
)


class RagModel:
    def __init__(self, vector_store: VectorStore, llm: BaseChatModel) -> None:
        self.vector_store = vector_store
        self.llm = llm

    async def get_response(self, message: str) -> str:
        if not message.strip():
            return ""
        complexity = await self.check_question(message)
        if complexity == "simple":
            logger.debug("Handling as a simple question.")
            simple_answer = await self.llm.ainvoke(
                simple_question.format_prompt(question=message)
            )
            return simple_answer.content.strip()
        rewritten_question = await self.rewrite_question(message)
        context = await self.search_vectorstore(rewritten_question)
        return await self.generate_answer(message, context)

    async def check_question(self, question: str) -> str:
        """Check the complexity of the question."""
        classification = await self.llm.ainvoke(
            check_question_prompt.format_prompt(question=question)
        )
        complexity = classification.content.strip()
        logger.debug(f"Complexity classification: {complexity}")
        try:
            result = json.loads(complexity)
            return result.get("complexity", "complex")
        except json.JSONDecodeError:
            logger.error(f"Invalid complexity response: {complexity}")
            return "complex"

    async def rewrite_question(self, question: str) -> str:
        """Rewrite question to optimize search."""
        rewritten = await self.llm.ainvoke(
            re_write_prompt.format_prompt(question=question)
        )
        return rewritten.content.strip()

    async def search_vectorstore(self, question: str) -> str:
        """Search for context in vector store."""
        results = await self.vector_store.vector_store.asimilarity_search(question, k=3)
        logger.debug(results)
        if not results:
            return ""
        return "\n".join([doc.page_content for doc in results])

    async def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using context."""
        answer = await self.llm.ainvoke(
            answer_prompt.format_prompt(question=question, context=context)
        )
        return answer.content.strip()
