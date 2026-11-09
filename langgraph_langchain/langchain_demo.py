from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
MODEL_NAME = "qwen2.5:3b-instruct"
def build_simple_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a concise travel assistant. Answer in 2-3 sentences.",
            ),
            ("human", "{query}"),
        ]
    )
    llm = ChatOllama(model=MODEL_NAME, temperature=0.3)    
    chain = prompt | llm
    return chain
def run_demo():
    chain = build_simple_chain()
    query = "What are 3 must-see attractions in Chennai?"
    response = chain.invoke({"query": query})
    print("=== LangChain-only demo ===")
    print(f"User query : {query}")
    print(f"LLM response: {response.content}")
if __name__ == "__main__":
    run_demo()
