from prompts import INQUIRY_SYSTEM_PROMPT


agent = {
    "name": "inquiry-agent",
    "description": """You are the 'Soul Painter' (Inquiry Agent). Your goal is to map the story's soul through a series of "Dramatic Choices".""",
    "system_prompt": INQUIRY_SYSTEM_PROMPT,
    "model": "deepseek-chat",  # Optional override, defaults to main agent model
}
