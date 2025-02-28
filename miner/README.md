# Bitcoin Miner Client

## Overview
This project is a **Bitcoin Miner Client** that connects to a **Bitcoin Miner Pool** and performs mining using a multiprocessing approach. It follows an optimized workflow to ensure efficiency and reliability in mining operations.

### Features:
- **Multiprocessing Support**: Distributes mining workload across multiple CPU cores.
- **WebSocket Connection**: Connects to the mining pool server to receive job data.
- **Mining Process Management**: Efficiently handles mining work and submits valid solutions.
- **Automatic Reconnection**: Handles connection losses and attempts to reconnect.
- **Graceful Shutdown**: Listens for shutdown signals and terminates mining operations cleanly.

## Process Flow
![Process Flow](images/miner-flow.png)

## Getting Started

### Prerequisites
Ensure you have the following installed before proceeding:
- **Python 3.10**
- **Docker & Docker Compose** (if running via Docker)
- **Git**

### Running with Docker
To run the miner using Docker, simply execute:
```sh
make docker-compose-up
```
This command will:
- Start the miner client.
- Connect to the mining pool server.
- Begin mining operations.

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
4. Run the miner client:
   ```sh
   python main.py
   ```

## Configuration
This project uses an `.env` file for configuration. Ensure you update it with the appropriate values before running the project.



## Deployment & Optimization
- **Performance Tuning**: Optimize mining threads for better CPU utilization.
- **Monitoring**: Implement logging to track mining statistics.
- **Scaling**: Run multiple miner instances across different machines.

## One-Click Go Solution
This setup provides a **one-click go solution** for running a Bitcoin miner. Simply execute the required command (Docker or non-Docker), and the miner will start working!

## Author
**Rohit Nishad**  
GitHub: [merohitnishad](https://github.com/merohitnishad)  
Website: [rohitnishad.com](https://rohitnishad.com/)  
LinkedIn: [merohitnishad](https://www.linkedin.com/in/merohitnishad/)