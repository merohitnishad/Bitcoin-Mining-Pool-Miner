# Load environment variables
from dotenv import load_dotenv

load_dotenv()

import asyncio
import json
import logging
import signal
import os
import multiprocessing

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from src.lib.miner import solve_block
from src.helpers.logger import logger
from src.helpers.setup import setup_environment

SERVER_URL = os.getenv("SERVER_URL")


class ConnectionManager:
    def __init__(self, server_url):
        """
        Initialize ConnectionManager with server URL and necessary attributes.
        """
        self.server_url = server_url
        self.websocket = None
        self.solve_task = None
        self.keep_alive_task = None
        self.start = 0
        self.end = 4294967296  # 2^32

    async def establish_connection(self):
        """
        Establish a persistent WebSocket connection with the server.
        Reconnects if the connection fails.
        """
        while True:
            try:
                self.websocket = await websockets.connect(self.server_url)
                logger.info("Connected to server")
                return
            except (ConnectionRefusedError, OSError) as e:
                logger.error(
                    f"Connection attempt failed: {e}. Retrying in 10 seconds..."
                )
                await asyncio.sleep(10)

    async def handle_server_messages(self):
        """
        Listen for messages from the server and handle them accordingly.
        """
        try:
            async for message in self.websocket:
                message_data = json.loads(message)
                event = message_data.get("event")
                msg = message_data.get("message")

                if event == "height_changed":
                    await self.handle_height_changed(msg)
                elif event == "range_assignment":
                    await self.handle_range_assignment(msg)
        except (ConnectionClosedError, ConnectionClosedOK):
            logger.warning("Connection closed. Reconnecting...")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    async def send_message(self, event, message):
        """
        Send a message to the WebSocket server if connected.
        """
        if self.is_connected():
            message_json = json.dumps({"event": event, "message": message})
            await self.websocket.send(message_json)
        else:
            logger.warning("Attempted to send message, but WebSocket is not connected")

    async def send_nonce_found(self, nonce):
        """
        Notify the server when a nonce is found.
        """
        await self.send_message("nonce_found", nonce)

    async def send_iteration_completed(self, iteration):
        """
        Notify the server when an iteration is completed.
        """
        await self.send_message("iteration_completed", iteration)

    async def handle_range_assignment(self, message):
        """
        Handle the range assignment message from the server.
        """
        logger.info(f"Setting range assignment: {message}")
        self.start = message["start"]
        self.end = message["end"]

    async def handle_height_changed(self, tmpl):
        """
        Handle changes in block height and restart solving task if needed.
        """
        if self.solve_task and not self.solve_task.done():
            self.solve_task.cancel()
        self.solve_task = asyncio.create_task(self.solve_block_task(tmpl))

    async def solve_block_task(self, tmpl):
        """
        Solve the block using the assigned range and template.
        """
        logger.info(f"Start & end: {self.start}, {self.end}")
        try:
            while True:
                if not self.is_connected():
                    logger.warning(
                        "WebSocket disconnected, cancelling solve_block task"
                    )
                    break
                nonce = await asyncio.to_thread(
                    solve_block,
                    tmpl["version"],
                    tmpl["prev_block"],
                    tmpl["mrkl_root"],
                    tmpl["timestamp"],
                    tmpl["bits_difficulty"],
                    self.start,
                    self.end,
                )
                if nonce != "xxx":
                    logger.info(f"Sending nonce: {nonce}")
                    await self.send_nonce_found(
                        {"nonce": nonce, "timestamp": tmpl["timestamp"]}
                    )
                    break
                else:
                    tmpl["timestamp"] += 1
                    logger.info(
                        "Iteration finished, incrementing timestamp and retrying"
                    )
        except asyncio.CancelledError:
            logger.warning(
                "Task cancelled. Restarting solve_block with new parameters."
            )
        except Exception as e:
            logger.error(f"Error in solving block: {e}")

    async def keep_alive(self):
        """
        Send periodic ping messages to keep the WebSocket connection alive.
        """
        try:
            while True:
                if self.is_connected():
                    await self.send_message("ping", 1)
                else:
                    logger.warning(
                        "Keep-alive ping skipped, WebSocket is not connected"
                    )
                await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")

    async def connect_to_server(self):
        """
        Establish a connection and manage tasks for handling messages and keeping alive.
        """
        while True:
            await self.establish_connection()
            receive_task = asyncio.create_task(self.handle_server_messages())
            self.keep_alive_task = asyncio.create_task(self.keep_alive())

            done, pending = await asyncio.wait(
                [receive_task, self.keep_alive_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            logger.info("Reconnecting to the server in 10 seconds...")
            await asyncio.sleep(10)

    def is_connected(self):
        """
        Check if the WebSocket is connected.
        """
        return self.websocket is not None and self.websocket.open


async def main():
    """
    Main function to initialize and start the ConnectionManager.
    """
    setup_environment()
    manager = ConnectionManager(SERVER_URL)

    loop = asyncio.get_running_loop()

    def shutdown():
        """
        Handle shutdown signals gracefully.
        """
        tasks = asyncio.all_tasks()
        for task in tasks:
            task.cancel()
        logger.info("Shutting down miner...")

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    try:
        await manager.connect_to_server()
    except asyncio.CancelledError:
        logger.info("Miner shutting down.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Set the start method to spawn to ensure Manager connections work correctly in Docker
    multiprocessing.set_start_method("spawn", force=True)
    asyncio.run(main())
