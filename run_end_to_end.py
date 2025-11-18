"""
Run the entire multi-agent system end-to-end.
Starts the MCP server, A2A servers, initializes agents, and runs test queries.
"""

import asyncio
from a2a.a2a_client import A2ASimpleClient
from agents.customer_data_agent import create_customer_data_agent
from agents.support_agent import create_support_agent
from agents.router_agent import create_router_agent
from a2a.start_a2a_servers import start_servers

# MCP URL should be your ngrok or localhost URL
MCP_URL = "http://127.0.0.1:5000/mcp"

# Create agents
customer_data_agent = create_customer_data_agent(MCP_URL)
support_agent = create_support_agent()
router_agent, router_card = create_router_agent()

# Start A2A servers
start_servers([
    (customer_data_agent, customer_data_card(), 11020),
    (support_agent, support_agent_card(), 11021),
    (router_agent, router_card, 11022),
])

client = A2ASimpleClient()
ROUTER_URL = "http://127.0.0.1:11022"

async def main():
    print(await client.create_task(ROUTER_URL, "I need help with my account, customer ID 5"))
    print(await client.create_task(ROUTER_URL, "I want to cancel my subscription but I'm having billing issues."))
    print(await client.create_task(ROUTER_URL, "Show me all active customers who have open tickets."))

if __name__ == "__main__":
    asyncio.run(main())
