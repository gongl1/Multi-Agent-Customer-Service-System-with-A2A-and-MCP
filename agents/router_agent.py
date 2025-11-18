from a2a.types import AgentCard, AgentCapabilities, TransportProtocol
from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

def create_router_agent():
    # Remote wrappers
    remote_data = RemoteA2aAgent(
        name="customer_data_remote",
        description="Remote Customer Data Agent",
        agent_card=f"http://127.0.0.1:11020{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    remote_support = RemoteA2aAgent(
        name="support_remote",
        description="Remote Support Agent",
        agent_card=f"http://127.0.0.1:11021{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    router_agent = SequentialAgent(
        name="customer_service_router",
        sub_agents=[remote_data, remote_support],
    )

    router_card = AgentCard(
        name="Customer Service Router",
        url="http://127.0.0.1:11022",
        description="Coordinates support & database specialist agents.",
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[],
    )

    return router_agent, router_card
