# Load environment variables
from dotenv import load_dotenv

load_dotenv()


import os
from src.helpers.btc_util import create_coinbase
from src.lib.rpc import rpc_getblocktemplate, rpc_submitblock
from test_framework.blocktools import add_witness_commitment, create_block
from src.helpers.logger import logger

# Load environment variables

PUBLIC_KEY = os.getenv("MINER_PUBLIC_KEY")


def main():
    try:
        # Retrieve the current block template from the node
        tmpl = rpc_getblocktemplate()
        if not tmpl:
            logger.error("Failed to get block template")
            return

        logger.info(f"Current blockchain height: {tmpl['height']}")
        logger.info(f"Mining to address: {PUBLIC_KEY}")

        # Determine the coinbase transaction value
        coinbase_amount = min(5000000000, tmpl["coinbasevalue"])
        logger.info(f"Coinbase amount: {coinbase_amount}")

        # Create the coinbase transaction
        coinbase_transaction = create_coinbase(
            tmpl["height"], coinbase_amount, PUBLIC_KEY
        )
        logger.info("Coinbase transaction created successfully")

        # Collect transaction hashes up to a limit of 800 transactions
        txhases = []
        txn_count = 0

        for txn in tmpl["transactions"]:
            txhases.append(txn["data"])
            txn_count += 1
            if txn_count >= 800:
                break

        logger.info(f"Included {txn_count} transactions in the block")

        # Create the block with the coinbase and transactions
        block = create_block(coinbase=coinbase_transaction, tmpl=tmpl, txlist=txhases)
        add_witness_commitment(block=block)

        # Solve the block by finding a valid nonce
        block.solve()
        serialized_hex = block.serialize().hex()

        logger.info(f"Block solved with nonce: {block.nNonce}")

        # Submit the block to the network
        result = rpc_submitblock(serialized_hex)
        logger.info(f"Block submission result: {result}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
