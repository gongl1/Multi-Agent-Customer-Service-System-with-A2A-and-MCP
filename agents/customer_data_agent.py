from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

def create_customer_data_agent(mcp_url: str):
    return LlmAgent(
        model="gemini-2.5-flash",
        name="customer_data_agent",
        description="""
Customer Data Agent:
- Uses MCP tools only.
- Tools: get_customer, list_customers, update_customer,
         create_ticket, get_customer_history.
- Returns structured JSON summaries.
""",
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(url=mcp_url)
            )
        ],
    )
