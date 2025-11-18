from a2a.types import AgentCard, AgentCapabilities, TransportProtocol

def customer_data_card():
    return AgentCard(
        name="Customer Data Agent",
        url="http://127.0.0.1:11020",
        description="Specialist for customer DB via MCP.",
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[],
    )

def support_agent_card():
    return AgentCard(
        name="Support Agent",
        url="http://127.0.0.1:11021",
        description="General customer support agent.",
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[],
    )
