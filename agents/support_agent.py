from google.adk.agents import LlmAgent

def create_support_agent():
    return LlmAgent(
        model="gemini-2.5-flash",
        name="support_agent",
        description="""
Support Agent:
- Handles general customer support.
- Does NOT call MCP directly.
- Uses context passed from the Router/Data Agent.
- Escalates urgent issues.
""",
    )
