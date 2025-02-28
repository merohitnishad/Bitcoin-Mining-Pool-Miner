# Load environment variables
from dotenv import load_dotenv

load_dotenv()


import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
import websockets
import os
from src.helpers.btc_util import create_mining_block, get_mining_template
from src.lib.rpc import publish_block, rpc_getblockchaininfo, rpc_getblocktemplate
from src.helpers.logger import logger
from src.helpers.setup import setup_environment


class ConnectionManager:
    def __init__(self):
        """Initialize connection manager with required attributes."""
        self.connected_clients = set()
        self.current_height = None
        self.block = None
        self.executor = ThreadPoolExecutor()
        self.start = 0
        self.end = 4294967296
        self.mining_info = None

    async def register(self, websocket):
        """Register a new WebSocket client."""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

    async def unregister(self, websocket):
        """Unregister a WebSocket client when disconnected."""
        if websocket in self.connected_clients:
            self.connected_clients.remove(websocket)
            logger.info(
                f"Client disconnected. Total clients: {len(self.connected_clients)}"
            )

    async def send_message(self, websocket, event, message):
        """Send a JSON message to a specific WebSocket client."""
        message_json = json.dumps({"event": event, "message": message})
        await websocket.send(message_json)

    async def send_message_to_all(self, event, message):
        """Broadcast a JSON message to all connected clients."""
        if self.connected_clients:
            message_json = json.dumps({"event": event, "message": message})
            await asyncio.gather(
                *[client.send(message_json) for client in self.connected_clients]
            )

    async def handle_client(self, websocket, path):
        """Handle incoming WebSocket connections."""
        await self.register(websocket)
        if self.mining_info is not None:
            logger.info(f"Sending mining info to {len(self.connected_clients)} clients")
            await self.divide_range_among_clients()
            await self.send_message(websocket, "height_changed", self.mining_info)

        try:
            async for message in websocket:
                message_data = json.loads(message)
                event = message_data.get("event")
                msg_content = message_data.get("message")

                # Event handler mapping
                event_handler = {
                    "nonce_found": self.handle_nonce_found,
                    "ping": self.ping,
                }

                handler = event_handler.get(event)
                if handler:
                    await handler(websocket, msg_content)
                else:
                    logger.warning(f"Received unknown event: {event}")

        except websockets.ConnectionClosed:
            logger.warning("Client connection closed unexpectedly")
        finally:
            await self.unregister(websocket)

    async def check_api(self):
        """Periodically check the blockchain for height changes and update mining templates."""
        while True:
            try:
                blockchain_info = await asyncio.get_event_loop().run_in_executor(
                    self.executor, rpc_getblockchaininfo
                )
                height = blockchain_info.get("blocks")

                if height is not None and height != self.current_height:
                    self.current_height = height
                    tmpl = await asyncio.get_event_loop().run_in_executor(
                        self.executor, rpc_getblocktemplate
                    )
                    block = create_mining_block(tmpl)
                    self.block = block

                    mining_info = get_mining_template(block)
                    self.mining_info = mining_info

                    logger.info(f"Blockchain height changed to {height}")

                    if self.connected_clients:
                        logger.info("Sending new mining block template to clients")
                        await self.divide_range_among_clients()
                        await self.send_message_to_all(
                            "height_changed", self.mining_info
                        )
                    else:
                        logger.info("No connected clients to send block template")

            except Exception as e:
                logger.error(f"Error while checking blockchain API: {e}")

            await asyncio.sleep(5)  # Wait before next API check

    async def handle_nonce_found(self, websocket, message):
        """Process a found nonce from a client."""
        nonce = message.get("nonce")
        timestamp = message.get("timestamp")

        if nonce is not None:
            logger.info(f"Received valid nonce from client: {message}")
            self.block.nNonce = nonce
            self.block.nTime = timestamp
            self.block.rehash()

            if self.block.is_valid():
                logger.info("Block is valid and ready for submission")
                publish_block(self.block, self.current_height)
            else:
                logger.warning(f"Invalid nonce received: {message}")
        else:
            logger.warning("Received invalid nonce message")

    async def ping(self, websocket, message):
        """Respond to ping messages from clients."""
        await self.send_message(websocket, "ping", f"Ping back: {message}")

    async def divide_range_among_clients(self):
        """Distribute the mining nonce search range among connected clients."""
        num_clients = len(self.connected_clients)
        if num_clients == 0:
            return

        total_range = self.end - self.start
        range_per_client = total_range // num_clients
        client_ranges = []

        current_start = self.start
        for i in range(num_clients):
            current_end = current_start + range_per_client
            if i == num_clients - 1:
                current_end = (
                    self.end
                )  # Ensure the last client gets the remaining range
            client_ranges.append((current_start, current_end))
            current_start = current_end

        clients = list(self.connected_clients)
        for i, client in enumerate(clients):
            start, end = client_ranges[i]
            await self.send_message(
                client, "range_assignment", {"start": start, "end": end}
            )
            logger.info(f"Assigned range {start} - {end} to client")


async def main():
    """Start the WebSocket server and blockchain monitor task."""

    PORT = 8765  # WebSocket server port

    manager = ConnectionManager()
    server = await websockets.serve(manager.handle_client, "0.0.0.0", PORT)
    logger.info(f"WebSocket server started on port {PORT}")

    asyncio.create_task(manager.check_api())

    await server.wait_closed()


if __name__ == "__main__":
    setup_environment()
    asyncio.run(main())
