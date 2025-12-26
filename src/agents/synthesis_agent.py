from prompts import SYNTHESIS_SYSTEM_PROMPT


agent = {
    "name": "synthesis-agent",
    "description": """You are the Master Screenwriter (Synthesis Agent). You turn the captured soul into a professional-grade screenplay.""",
    "system_prompt": SYNTHESIS_SYSTEM_PROMPT,
    "model": "deepseek-chat",  # Optional override, defaults to main agent model
}
