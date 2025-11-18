import httpx
from typing import Any
from a2a.client import ClientConfig, ClientFactory, create_text_message_object
from a2a.types import AgentCard, TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

class A2ASimpleClient:
    def __init__(self, timeout: float = 240.0):
        self.cache = {}
        self.timeout = timeout

    async def create_task(self, agent_url: str, message: str):
        timeout_cfg = httpx.Timeout(
            timeout=self.timeout, connect=10.0, read=self.timeout, write=10.0
        )

        async with httpx.AsyncClient(timeout=timeout_cfg) as http:
            if agent_url not in self.cache:
                card = await http.get(f"{agent_url}{AGENT_CARD_WELL_KNOWN_PATH}")
                self.cache[agent_url] = card.json()

            agent_card = AgentCard(**self.cache[agent_url])

            config = ClientConfig(
                httpx_client=http,
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                use_client_preference=True,
            )

            client = ClientFactory(config).create(agent_card)

            msg = create_text_message_object(content=message)
            responses = [resp async for resp in client.send_message(msg)]

            if responses and isinstance(responses[0], tuple):
                task = responses[0][0]
                try:
                    return task.artifacts[0].parts[0].root.text
                except:
                    return str(task)

            return "No response."
