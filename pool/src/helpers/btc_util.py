import os
from test_framework.address import address_to_scriptpubkey
from test_framework.blocktools import (
    add_witness_commitment,
    create_block,
    script_BIP34_coinbase_height,
)
from test_framework.messages import COutPoint, CTransaction, CTxIn, CTxOut
from src.lib.rpc import rpc_getblocktemplate, rpc_submitblock
from src.helpers.logger import logger

# Load environment variables

PUBLIC_KEY = os.getenv("MINER_PUBLIC_KEY")


def create_coinbase(height, value, address):
    """Creates a coinbase transaction for the given block height and mining reward."""
    spk = address_to_scriptpubkey(address)
    cb = CTransaction()
    cb.vin = [
        CTxIn(
            COutPoint(0, 0xFFFFFFFF), script_BIP34_coinbase_height(height), 0xFFFFFFFF
        )
    ]
    cb.vout = [CTxOut(value, spk)]
    cb.vin[0].nSequence = 2**32 - 2
    cb.rehash()
    return cb


def create_mining_block(tmpl):
    """Creates a new mining block using the given template."""
    coinbase_transaction = create_coinbase(
        tmpl["height"], tmpl["coinbasevalue"], PUBLIC_KEY
    )

    txhases = []
    txn_count = 0

    for txn in tmpl["transactions"]:
        txhases.append(txn["data"])
        txn_count += 1
        if txn_count >= 800:
            break

    block = create_block(coinbase=coinbase_transaction, tmpl=tmpl, txlist=txhases)
    add_witness_commitment(block=block)
    return block


def get_mining_template(block):
    """Extracts and returns the essential mining data from the given block."""
    return {
        "version": block.nVersion,
        "prev_block": block.hashPrevBlock,
        "mrkl_root": block.hashMerkleRoot,
        "timestamp": block.nTime,
        "bits_difficulty": block.nBits,
    }
