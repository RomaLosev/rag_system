from langchain_core.prompts import PromptTemplate

grader_prompt = PromptTemplate(
    template="""You are a grader assessing whether an answer is grounded in / supported by a set of facts.\n
        Here are the facts:
        \n ------- \n
        {documents}
        \n ------- \n
        Here is the answer: {generation}
        Give a binary score 'yes' or 'no' score to indicate whether the answer is grounded in / supported by a set of facts.\n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
    input_variables=["generation", "documents"],
)


re_write_prompt = PromptTemplate(
    template="""You are a question re-writer that converts an input question to a better version optimized 
        for vectorstore retrieval. Ensure the language of the rewritten question is the same as the original question.
        
        Here is the initial question:
        {question}
        
        Improved question with no preamble:
        """,
    input_variables=["question"],
)

check_question_prompt = PromptTemplate(
    template="""You are a classifier that determines whether a user's question requires complex reasoning and additional data retrieval or can be answered directly without external resources.
        Сlassify any message containing a question as '"complex"' 
        Here is the user's question: {question}
    
        If the question is simple (e.g., a general or straightforward fact), respond with a JSON containing a single key `"complexity"` with the value `"simple"`.
        If the question requires external data, advanced reasoning, or multiple pieces of information, respond with a JSON containing `"complexity"`: `"complex"`.
        Provide no other explanation or text. Do not include any preamble, explanation, or additional formatting, such as backticks or code blocks.""",
    input_variables=["question"],
)

answer_prompt = PromptTemplate(
    template="""You are a helpful and detailed assistant providing structured, accurate, and context-aware answers. 
        Use the provided context to thoroughly answer the user's question. Ensure your response is detailed, well-structured, and divided into sections.
        Include examples, specific details, and references to the context where applicable. 

        Important! Always respond in the **exact same language as the question**. For example, if the question is in Russian, respond in Russian. 

        Context:
        {context}

        Question:
        {question}

        Answer:

        [Provide a clear and concise definition or explanation.]

        1. [Aspect 1 with details and examples.]
        2. [Aspect 2 with explanation and relevance.]
        3. [Aspect 3 if applicable.]

        [Summarize the key points and their significance.]
        """,
    input_variables=["context", "question"],
)

simple_question = PromptTemplate(
    template="Respond in the same language as the question. Question: {question}\n\nProvide a short and direct answer to the user question.",
    input_variables=["question"]
)
