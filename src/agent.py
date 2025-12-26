from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from tools.internet_search import internet_search
from prompts import (
    SYSTEM_PROMPT,
)
from tools.speech import azure_speech_synthesis_tool

load_dotenv()

llm = init_chat_model("deepseek-chat")

tools = [internet_search, azure_speech_synthesis_tool]

agent = create_deep_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)
