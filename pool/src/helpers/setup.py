import os


from src.helpers.logger import logger


def setup_environment() -> None:
    """
    Validate additional environment variables and perform initial setup.
    Raises an error if required environment variables are missing.
    """
    required_vars = ["RPC_URL", "RPC_USER", "RPC_PASS", "MINER_PUBLIC_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    logger.info("RPC_URL " + os.getenv("RPC_URL", ""))
    logger.info("MINER_PUBLIC_KEY " + os.getenv("MINER_PUBLIC_KEY", ""))
