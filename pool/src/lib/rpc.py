import base64
import json
import random
import urllib.request

import os


from src.lib.inform import inform_me
from src.helpers.logger import logger


# Retrieve RPC credentials from environment variables
RPC_URL = os.getenv("RPC_URL")
RPC_USER = os.getenv("RPC_USER")
RPC_PASS = os.getenv("RPC_PASS")


def rpc(method, params=None):
    """
    Make an RPC call to the Bitcoin Daemon JSON-HTTP server.
    :param method: The RPC method to call.
    :param params: Parameters for the RPC method.
    :return: The result of the RPC call.
    """
    try:
        rpc_id = random.getrandbits(32)  # Generate a random ID for the request
        data = json.dumps({"id": rpc_id, "method": method, "params": params}).encode()
        auth = base64.b64encode(f"{RPC_USER}:{RPC_PASS}".encode()).decode().strip()

        request = urllib.request.Request(
            RPC_URL, data, {"Authorization": f"Basic {auth}"}
        )

        logger.info(f"Sending RPC request: {method}")

        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read())

        # Validate the response ID
        if result["id"] != rpc_id:
            raise ValueError(
                f"Invalid response ID: got {result['id']}, expected {rpc_id}"
            )

        # Check if an error occurred
        if result["error"] is not None:
            raise ValueError(f"RPC error: {json.dumps(result['error'])}")

        logger.info(f"RPC call successful: {method}")
        return result["result"]
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to {RPC_URL}: {e}")
        raise ConnectionError(f"Failed to connect to {RPC_URL}: {e}")
    except Exception as e:
        logger.error(f"RPC call failed: {e}")
        raise RuntimeError(f"RPC call failed: {e}")


def rpc_getblocktemplate():
    """
    Get the block template for mining.
    :return: Block template JSON response.
    """
    try:
        return rpc("getblocktemplate", [{"rules": ["segwit"]}])
    except ValueError as e:
        logger.error(f"Error getting block template: {e}")
        return {}


def rpc_getblockchaininfo():
    """
    Retrieve information about the blockchain.
    :return: Blockchain info JSON response.
    """
    try:
        return rpc("getblockchaininfo")
    except ValueError as e:
        logger.error(f"Error getting blockchain info: {e}")
        return {}


def rpc_submitblock(block_submission):
    """
    Submit a mined block to the network.
    :param block_submission: Serialized block in hex format.
    :return: Response from the RPC server.
    """
    try:
        logger.info("Submitting block...")
        return rpc("submitblock", [block_submission])
    except Exception as e:
        logger.error(f"Error submitting block: {e}")
        inform_me(f"Error submitting block: {e}")
        return None


def publish_block(block, height):
    """
    Publish a mined block to the blockchain.
    :param block: The block object.
    :param height: The height of the block in the blockchain.
    :return: RPC response or None if submission fails.
    """
    try:
        serialized_hex = block.serialize().hex()  # Convert block to hex format
        result = rpc_submitblock(serialized_hex)
        logger.info("Block submitted successfully")
        inform_me(f"Block Mined\nBlock Height: {height}\nBlock Hash: {block.hash}")
        return result
    except Exception as e:
        logger.error(f"Failed to publish block: {e}")
        return None
