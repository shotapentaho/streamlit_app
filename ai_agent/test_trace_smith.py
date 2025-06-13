from langchain_openai import ChatOpenAI


LANGSMITH_TRACING=True
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="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"
LANGSMITH_PROJECT="hello-test-tracing-langsmith"
OPENAI_API_KEY="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"


llm = ChatOpenAI()
llm.invoke("Hello, world!")
