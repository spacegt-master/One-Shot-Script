from prompts import AUDIO_SYSTEM_PROMPT

# --- 2. 配置 Audio Agent ---
agent = {
    "name": "audio-agent",
    "description": """
    The Professional Audio Director Agent using Azure Speech SDK. 
    1. It analyzes the screenplay to create a 'Voice To-Do List' and a technical JSON manifest.
    2. IMMEDIATELY after generating the manifest, it MUST call 'azure_speech_synthesis_tool' to produce broadcast-quality .mp3 files.
    3. It updates '音频配置清单.md' with the final synthesis status and file locations.
    """,
    "system_prompt": AUDIO_SYSTEM_PROMPT,
    "model": "deepseek-chat",
}
