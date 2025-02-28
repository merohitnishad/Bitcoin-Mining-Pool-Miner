# Bitcoin Node Setup in Regtest Mode

## Prerequisites

Ensure you have the following dependencies installed on your system:

* Linux/macOS/Windows (with WSL if needed)
* Bitcoin Core ([Download Here](https://bitcoincore.org/en/download/))

## Step 1: Install Bitcoin Core

Download and install Bitcoin Core from the official website. Extract and install the binaries.

### For Linux/macOS:

```sh
wget https://bitcoincore.org/bin/bitcoin-core-25.0/bitcoin-25.0-x86_64-linux-gnu.tar.gz

# Extract and install
tar -xvf bitcoin-25.0-x86_64-linux-gnu.tar.gz
cd bitcoin-25.0
sudo install -m 0755 -o root -g root -t /usr/local/bin bin/*
```

### For Windows:

1. Download and install Bitcoin Core.
2. Add the installation directory (where `bitcoind` and `bitcoin-cli` are located) to your system's PATH.

## Step 2: Configure Bitcoin Node RPC Settings

To configure the node with a custom username, password, and port, edit the `bitcoin.conf` file.

### Create/Edit `bitcoin.conf`

Locate or create the configuration file:

```sh
mkdir -p ~/.bitcoin
nano ~/.bitcoin/bitcoin.conf
```

Add the following lines to set the RPC username, password, and port:

```
regtest=1
rpcuser=yourusername
rpcpassword=yourpassword
rpcport=18443
```

Save and exit the file.

## Step 3: Run Bitcoin Node in Regtest Mode

Regtest mode allows you to run a local Bitcoin network for development and testing.

### Start Bitcoin Core in Regtest Mode:

```sh
bitcoind -regtest -daemon
```

This runs the Bitcoin daemon in the background.

## Step 4: Create a Wallet

Generate a new wallet to store Bitcoin in the regtest environment.

```sh
bitcoin-cli -regtest createwallet "test_wallet"
```

## Step 5: Generate a New Bitcoin Address

Once the wallet is created, generate a new receiving address:

```sh
bitcoin-cli -regtest getnewaddress
```

This will return an address like:

```
n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi
```

Save this address for the next step.

## Step 6: Mine 101 Blocks to Your Address

Mining blocks will generate Bitcoin and confirm transactions.

```sh
bitcoin-cli -regtest generatetoaddress 101 "n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi"
```

This command mines 101 blocks to the given address. The first 100 blocks are required for coin maturity, so you can spend the Bitcoin.

## Step 7: Check Wallet Balance

To check the balance of your wallet:

```sh
bitcoin-cli -regtest getbalance
```

## Additional Commands

* **List all addresses in the wallet:**
  ```sh
  bitcoin-cli -regtest listreceivedbyaddress 0 true
  ```
* **Dump private key of an address:**
  ```sh
  bitcoin-cli -regtest dumpprivkey "n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi"
  ```
* **Send Bitcoin to another address:**
  ```sh
  bitcoin-cli -regtest sendtoaddress "destination_address" amount
  ```

## Stopping the Node

To stop Bitcoin Core, run:

```sh
bitcoin-cli -regtest stop
```

## Conclusion

You have successfully set up a Bitcoin node in regtest mode, configured RPC settings, created a wallet, mined blocks, and checked your balance. This is useful for development and testing Bitcoin-related applications locally without using real Bitcoin.
