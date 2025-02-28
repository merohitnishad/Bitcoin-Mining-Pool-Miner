# Bitcoin Miner Pool

## Overview

This project is a **Bitcoin Miner Pool** that utilizes the Bitcoin Docker image to run a Bitcoin node and provide a block template for miners. It starts a **WebSocket server** that allows miners to connect and fetch the required data needed for mining.

### Features:

- **Bitcoin Node Integration**: Uses the Bitcoin Docker image to run a full Bitcoin node.
- **WebSocket Mining Pool**: Starts a WebSocket server to allow miners to connect.
- **Block Template Fetching**: Retrieves block templates from the Bitcoin node's RPC URL.
- **Block Submission**: Submits mined blocks to the Bitcoin node server.
- **Telegram Notifications**: Notifies the user via Telegram chat when a block is successfully submitted to the Bitcoin blockchain.
- **Scalability**: Designed to handle multiple miner connections simultaneously.
- **Efficiency Optimized**: Implements optimized block template generation for improved mining efficiency.

## Process Flow

![Process Flow](images/pool-flow.png)

## Getting Started

### Prerequisites

Ensure you have the following installed before proceeding:

- **Python 3.10**
- **Docker & Docker Compose**
- **Git**

### Running with Docker

To run the project using Docker, simply execute:

```sh
make docker-compose-up
```

This command will:

- Start a Bitcoin node server.
- Start the mining pool server.
- Allow miners to connect and start mining.

### Running without Docker

For a non-Docker environment, follow these steps:

1. Copy the environment file:
   ```sh
   cp .env.example .env
   ```
2. Install dependencies:
   ```sh
   make install
   ```
3. Activate the virtual environment:
   ```sh
   source venv/bin/activate
   ```
4. Run the mining pool server:
   ```sh
   python main.py
   ```

## Configuration

This project uses an `.env` file for configuration. Ensure you update it with the appropriate values before running the project.

## Deployment & Optimization

- **Performance Tuning**: Optimize WebSocket handling and ensure minimal latency.
- **Monitoring**: Use logging and monitoring tools to track performance and errors.
- **Scaling**: Deploy across multiple instances to support high miner connections.

## One-Click Go Solution

This setup provides a **one-click go solution** for running a Bitcoin mining pool. Simply execute the required command (Docker or non-Docker), and your pool will be up and running!

## Author

**Rohit Nishad**
GitHub: [merohitnishad](https://github.com/merohitnishad)
Website: [rohitnishad.com](https://rohitnishad.com/)
LinkedIn: [merohitnishad](https://www.linkedin.com/in/merohitnishad/)
