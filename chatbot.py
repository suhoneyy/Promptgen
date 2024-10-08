import openai
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

# Set up OpenAI API
openai.api_key = "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"  # Replace with your OpenAI API key

# Define a storage for chat history
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Define the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Updated language model function (GPT-3.5 Turbo)
def gpt_3_5_turbo(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    print("Received from GPT-3.5 Turbo:", response.choices[0].message["content"])
    return AIMessage(content=response.choices[0].message["content"])

model = gpt_3_5_turbo

# Define a trimmer to manage conversation history
trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=model,  # Use the model to count tokens
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# Create the main chatbot chain
chain = (
    RunnablePassthrough.assign(messages=itemgetter("messages") | trimmer)
    | prompt
    | model
)

# Wrap the chain with message history
with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages",
)

# Define a function to interact with the chatbot
def chat_with_bot(session_id, user_input, language="English"):
    config = {"configurable": {"session_id": session_id}}
    
    response = with_message_history.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "language": language,
        },
        config=config,
    )
    
    return response.content

# Run the chatbot
if __name__ == "__main__":
    session_id = "abc123"  # Replace with your session ID logic
    print("Chatbot is running...")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        response = chat_with_bot(session_id, user_input)
        print(f"Bot: {response}")
