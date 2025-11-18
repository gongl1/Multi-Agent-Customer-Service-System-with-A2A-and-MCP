import asyncio
import threading
import time

from .a2a_server_helpers import run_agent_server

def start_servers(agents_cards_ports):
    async def launcher():
        tasks = [
            asyncio.create_task(run_agent_server(agent, card, port))
            for (agent, card, port) in agents_cards_ports
        ]
        await asyncio.sleep(2)
        print("A2A servers running:")
        for (_, card, port) in agents_cards_ports:
            print(f" - {card.name}: http://127.0.0.1:{port}")
        await asyncio.gather(*tasks)

    def bg():
        asyncio.run(launcher())

    thread = threading.Thread(target=bg, daemon=True)
    thread.start()
    time.sleep(3)
